"""특강 프로그램: 모집 공고, 예약 신청(회원/비회원), 결제, 관리자 화면"""
import csv
import logging
import re
import time
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.core import signing
from django.core.cache import cache
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .parent_notify import _is_configured, _normalize_phone, _post_alimtalk, _spawn
from .models import (
    ParentChildLink, SpecialLecture, SpecialLectureCoupon, SpecialLectureImage, SpecialLectureParticipant, SpecialLectureReservation,
)

MAX_PARTICIPANTS = 6
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------- 카카오 알림톡
def _alimtalk_variables(res, with_amount=True):
    lecture = res.lecture
    when = timezone.localtime(lecture.lecture_at)
    when_label = f'{when.month}월 {when.day}일({"월화수목금토일"[when.weekday()]}) {when:%H:%M}'
    if lecture.end_time:
        when_label += f'~{lecture.end_time:%H:%M}'
    variables = {
        '#{신청자}': res.applicant_name,
        '#{특강명}': lecture.title,
        '#{일시}': when_label,
        '#{장소}': lecture.location_short or '메듀랩',
        '#{참가자}': ', '.join(res.participants.values_list('name', flat=True)),
    }
    if with_amount:
        variables['#{결제금액}'] = f'{res.amount:,}원' if res.amount else '무료'
    if settings.SOLAPI_SPECIAL_BUTTON_CODE:
        variables['#{예약코드}'] = res.token   # 버튼 주소 끝에 붙는 값
    if settings.SOLAPI_SPECIAL_INCLUDE_URL:
        variables['#{확인주소}'] = settings.SITE_BASE_URL.rstrip('/') + reverse('special_reservation', args=[res.token])
    return variables


def _deliver_alimtalk(res, template, with_amount):
    """알림톡 1건 발송 → (성공 여부, 상세). 설정이 비어 있으면 보내지 않고 이유를 돌려준다"""
    phone = _normalize_phone(res.phone)
    if not phone:
        return False, '수신 번호가 올바르지 않아 발송하지 않음'
    if not _is_configured(template):
        return False, '알림톡 설정(템플릿 ID) 미완료로 발송하지 않음'
    return _post_alimtalk(phone, template, _alimtalk_variables(res, with_amount))


def _send_confirmation_now(reservation_id):
    """예약 확정 안내 알림톡을 신청자 연락처로 보낸다 (결과는 예약 기록에 남기고, 실패해도 예약에는 영향 없음)"""
    from django.db import close_old_connections

    try:
        res = SpecialLectureReservation.objects.select_related('lecture').get(pk=reservation_id)
        if res.notified_at:
            return
        ok, detail = _deliver_alimtalk(res, settings.SOLAPI_TEMPLATE_SPECIAL, with_amount=True)
        res.notify_detail = detail[:300]
        if ok:
            res.notified_at = timezone.now()
        res.save(update_fields=['notified_at', 'notify_detail'])
    except Exception:
        logger.exception('특강 예약 알림톡 처리 중 오류')
    finally:
        close_old_connections()


def notify_confirmed(reservation):
    """예약이 확정되면 카카오 알림톡을 보내고 관리자에게 알린다. 외부 API 대기가 화면 응답을 늦추지 않도록 별도 스레드에서 처리한다."""
    _spawn(_send_confirmation_now, reservation.pk)
    notify_admin(reservation, '예약 확정')


def send_reminders(lecture):
    """특강 하루 전 안내 알림톡: 확정된 예약 중 아직 안내하지 않은 건에 보낸다 → (발송, 실패, 이유 목록)"""
    sent = failed = 0
    reasons = []
    for res in lecture.reservations.filter(status=SpecialLectureReservation.STATUS_CONFIRMED, reminder_sent_at__isnull=True):
        ok, detail = _deliver_alimtalk(res, settings.SOLAPI_TEMPLATE_SPECIAL_REMINDER, with_amount=False)
        if ok:
            res.reminder_sent_at = timezone.now()
            res.save(update_fields=['reminder_sent_at'])
            sent += 1
        else:
            failed += 1
            if detail not in reasons:
                reasons.append(detail)
    return sent, failed, reasons


# ---------------------------------------------------------------- 관리자 이메일 알림
def _send_admin_mail(reservation_id, label):
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.db import close_old_connections

    try:
        res = SpecialLectureReservation.objects.select_related('lecture').get(pk=reservation_id)
        recipients = settings.SPECIAL_NOTIFY_EMAILS or list(
            User.objects.filter(is_superuser=True, is_active=True).exclude(email='').values_list('email', flat=True))
        if not recipients:
            return
        people = ', '.join(res.participants.values_list('name', flat=True))
        body = (f'[{label}] {res.lecture.title}\n\n신청자: {res.applicant_name} ({res.phone})\n참가자: {people}\n'
                f'금액: {res.amount:,}원\n\n관리 화면: ' + settings.SITE_BASE_URL.rstrip('/')
                + reverse('special_admin_list') + f'?lecture={res.lecture_id}')
        send_mail(f'[메듀랩 특강] {label} - {res.lecture.title}', body,
                  getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@medulab.local'), recipients, fail_silently=True)
    except Exception:
        logger.exception('특강 신청 관리자 메일 처리 중 오류')
    finally:
        close_old_connections()


def notify_admin(reservation, label):
    _spawn(_send_admin_mail, reservation.pk, label)


# ---------------------------------------------------------------- 메듀랩 친구 확인
def is_medulab_student_name(name):
    """이름이 승인된 메듀랩 학생(재원생)과 일치하는지. 이름 외의 정보는 돌려주지 않는다"""
    from .models import UserProfile

    name = (name or '').strip()
    if not name:
        return False
    from django.db.models import Value
    from django.db.models.functions import Replace

    # 띄어쓰기 차이(박 재원 / 박재원)는 같은 이름으로 본다
    return UserProfile.objects.annotate(name_nospace=Replace('real_name', Value(' '), Value(''))).filter(
        user_type='medulab_member', is_approved=True, user__is_active=True, name_nospace=name.replace(' ', '')).exists()


def special_check_friend(request):
    """친구 이름 확인용 JSON. 이름 대입으로 재원생을 알아내는 것을 막기 위해 IP별로 횟수를 제한한다"""
    from django.core.cache import cache

    ip = (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', ''))
    key = f'special_friend_check_{ip}'
    count = cache.get(key, 0)
    if count >= 30:
        return JsonResponse({'verified': False, 'throttled': True}, status=429)
    cache.set(key, count + 1, 600)
    return JsonResponse({'verified': is_medulab_student_name(request.GET.get('name'))})


# ---------------------------------------------------------------- 쿠폰
def grant_welcome_coupon(user):
    """회원가입을 마친 회원에게 특강 1회 무료 참여 쿠폰을 한 장 지급한다 (이미 받았으면 지급하지 않음)"""
    coupon, created = SpecialLectureCoupon.objects.get_or_create(user=user, kind=SpecialLectureCoupon.KIND_WELCOME)
    return coupon if created else None


def available_coupon(user):
    """지금 쓸 수 있는 무료 쿠폰 한 장. 결제 대기 중인 신청에 묶여 있어도 30분이 지나면 다시 쓸 수 있다"""
    if not user.is_authenticated:
        return None
    hold_from = timezone.now() - timedelta(minutes=SpecialLecture.PENDING_HOLD_MINUTES)
    for coupon in user.special_coupons.filter(used_at__isnull=True).select_related('reservation'):
        res = coupon.reservation
        if (res is None or res.status == SpecialLectureReservation.STATUS_CANCELED
                or (res.status == SpecialLectureReservation.STATUS_PENDING and res.created_at < hold_from)):
            return coupon
    return None


# ---------------------------------------------------------------- 스팸 방지
MIN_FILL_SECONDS = 3


def _client_ip(request):
    return request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')


def make_form_token():
    """신청 화면을 연 시각을 서명해 폼에 넣는다 (너무 빠른 자동 제출을 걸러내는 용도)"""
    return signing.dumps(int(time.time()), salt='special-form')


def _spam_error(request):
    if request.POST.get('website'):   # 사람 눈에는 안 보이는 칸. 봇이 채우면 차단
        return '신청을 처리할 수 없어요.'
    try:
        issued = signing.loads(request.POST.get('form_token', ''), salt='special-form', max_age=6 * 3600)
    except signing.BadSignature:
        return '신청 화면이 만료되었어요. 화면을 새로 고친 뒤 다시 신청해 주세요.'
    if time.time() - issued < MIN_FILL_SECONDS:
        return '너무 빨리 제출되었어요. 잠시 뒤 다시 눌러 주세요.'
    if cache.get(f'special_apply_{_client_ip(request)}', 0) >= 8:
        return '짧은 시간에 신청이 너무 많아요. 잠시 뒤 다시 시도해 주세요.'
    return None


def _count_application(request):
    key = f'special_apply_{_client_ip(request)}'
    cache.set(key, cache.get(key, 0) + 1, 600)


def _live_participants(lecture, exclude_reservation=None):
    """자리를 차지하고 있는 참가자: 확정 + 결제 대기(30분 이내)"""
    from django.db.models import Q

    hold_from = timezone.now() - timedelta(minutes=SpecialLecture.PENDING_HOLD_MINUTES)
    qs = SpecialLectureParticipant.objects.filter(reservation__lecture=lecture).filter(
        Q(reservation__status=SpecialLectureReservation.STATUS_CONFIRMED)
        | Q(reservation__status=SpecialLectureReservation.STATUS_PENDING, reservation__created_at__gte=hold_from))
    return qs.exclude(reservation=exclude_reservation) if exclude_reservation else qs


def _already_applied(lecture, participants):
    """이미 신청(확정·결제대기·대기)된 같은 학생 이름 목록. 이름이 같고 생년월일도 같거나 알 수 없으면 같은 학생으로 본다"""
    from django.db.models import Q

    hold_from = timezone.now() - timedelta(minutes=SpecialLecture.PENDING_HOLD_MINUTES)
    base = SpecialLectureParticipant.objects.filter(reservation__lecture=lecture).filter(
        Q(reservation__status__in=[SpecialLectureReservation.STATUS_CONFIRMED, SpecialLectureReservation.STATUS_WAITLIST])
        | Q(reservation__status=SpecialLectureReservation.STATUS_PENDING, reservation__created_at__gte=hold_from))
    duplicated = []
    for p in participants:
        query = base.filter(name=p['name'])
        if p.get('birth_date'):
            query = query.filter(Q(birth_date=p['birth_date']) | Q(birth_date__isnull=True))
        if query.exists():
            duplicated.append(p['name'])
    return duplicated


def refund_reservation(reservation, reason):
    """포트원에 결제 취소(전액 환불)를 요청한다 → (성공 여부, 상세). 이미 취소된 결제도 성공으로 본다"""
    import requests

    if not settings.PORTONE_API_SECRET:
        return False, '결제 연동이 설정되지 않았어요'
    try:
        resp = requests.post(
            f'https://api.portone.io/payments/{reservation.portone_payment_id}/cancel',
            json={'reason': reason[:100]}, headers={'Authorization': f'PortOne {settings.PORTONE_API_SECRET}'}, timeout=15)
    except requests.RequestException as exc:
        return False, f'요청 오류: {exc}'[:300]
    if resp.status_code == 200 or (resp.status_code == 409 and 'ALREADY' in resp.text.upper()):
        reservation.refunded_at = timezone.now()
        reservation.refund_detail = '환불 완료'
        reservation.save(update_fields=['refunded_at', 'refund_detail'])
        return True, ''
    return False, f'HTTP {resp.status_code}: {resp.text}'[:300]


# ---------------------------------------------------------------- 참가자 / 가격
def is_medulab_parent(user):
    profile = getattr(user, 'profile', None) if user.is_authenticated else None
    return bool(profile and profile.user_type == 'medulab_parent' and profile.is_approved)


def parse_birth_date(raw):
    """2016.03.15 / 2016-03-15 / 20160315 형식의 생년월일을 날짜로. 형식이 틀리거나 미래면 None"""
    import datetime

    raw = (raw or '').strip()
    for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y%m%d', '%Y/%m/%d'):
        try:
            value = datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
        return value if datetime.date(1990, 1, 1) <= value <= datetime.date.today() else None
    return None


def parent_children_options(user):
    """메듀랩 학부모가 무료로 신청할 수 있는 자녀 목록 (연결된 학생 계정 + 가입 때 입력한 자녀 정보)"""
    from .forms import normalize_children_info

    options, seen = [], set()
    for link in ParentChildLink.objects.filter(parent=user).select_related('child__profile'):
        name = link.child.profile.real_name or link.child.username
        options.append({'key': f'u{link.child_id}', 'name': name, 'student_id': link.child_id, 'school': '', 'grade': '',
                        'birth_date': link.child.profile.birth_date, 'label': ''})
        seen.add(name)
    for index, child in enumerate(normalize_children_info(user.profile.children_info)):
        name = (child.get('name') or '').strip()
        if name and name not in seen:
            school, grade = (child.get('school') or '').strip(), (child.get('grade') or '').strip()
            options.append({'key': f'i{index}', 'name': name, 'student_id': None, 'school': school, 'grade': grade,
                            'birth_date': parse_birth_date(child.get('birth_date')), 'label': ' '.join(p for p in (school, grade) if p)})
    return options


def compute_pricing(lecture, participants, coupon=None, referral=False):
    """참가자별 참가비 계산. 친구 할인은 '2명 이상 함께 신청'하거나 '메듀랩에 다니는 친구를 적은 경우'에 1인당 적용되고,
    쿠폰은 첫 유료 참가자 1명을 무료로 한다.
    participants: [{'name', 'free', 'is_friend', ...}] → (같은 순서의 [{'price','note'}], 총액, 할인합계, 쿠폰사용여부)"""
    friend_deal = len(participants) >= 2 or bool(referral)
    rows = []
    for p in participants:
        if p['free']:
            rows.append({'price': 0, 'note': '메듀랩 수강생 무료'})
        elif friend_deal:
            rows.append({'price': max(lecture.base_price - lecture.friend_discount, 0), 'note': '친구 할인'})
        else:
            rows.append({'price': lecture.base_price, 'note': ''})

    coupon_used = False
    if coupon:
        paying = [i for i, r in enumerate(rows) if r['price'] > 0]
        first = next((i for i in paying if not participants[i].get('is_friend')), paying[0] if paying else None)
        if first is not None:
            rows[first] = {'price': 0, 'note': '무료 참여 쿠폰'}
            coupon_used = True

    total = sum(r['price'] for r in rows)
    list_total = lecture.base_price * sum(1 for p in participants if not p['free'])
    return rows, total, max(list_total - total, 0), coupon_used


def _clean_phone(raw):
    digits = re.sub(r'\D', '', raw or '')
    return digits if 9 <= len(digits) <= 11 else ''


def _person_from_fields(label, name, school, grade, birth, errors, is_friend):
    """이름·학교·학년·생년월일 4칸을 읽어 참가자 정보로. 빠진 칸이 있으면 errors에 안내를 추가하고 None"""
    name, school, grade, birth = (name or '').strip()[:50], (school or '').strip()[:50], (grade or '').strip()[:50], (birth or '').strip()
    missing = [t for t, v in (('이름', name), ('학교', school), ('학년', grade), ('생년월일', birth)) if not v]
    if missing:
        errors.append(f'{label}의 {", ".join(missing)}을(를) 입력해 주세요.')
        return None
    birth_date = parse_birth_date(birth)
    if not birth_date:
        errors.append(f'{label}의 생년월일 형식이 올바르지 않아요. (예: 2016.03.15)')
        return None
    return {'name': name, 'school': school, 'grade': grade, 'birth_date': birth_date, 'student_id': None,
            'is_friend': is_friend, 'free': False}


def _read_participants(request, lecture, user):
    """신청 폼에서 참가자 목록을 읽는다 → (participants, errors)"""
    errors, participants = [], []
    if is_medulab_parent(user):
        options = {o['key']: o for o in parent_children_options(user)}
        for key in request.POST.getlist('child'):
            option = options.get(key)
            if option:
                participants.append({'name': option['name'], 'school': option['school'], 'grade': option['grade'],
                                     'birth_date': option['birth_date'], 'student_id': option['student_id'],
                                     'is_friend': False, 'free': True})
        if not participants:
            errors.append('무료로 참여할 자녀를 한 명 이상 선택해 주세요.')
    else:
        person = _person_from_fields('참가하는 학생', request.POST.get('p_name'), request.POST.get('p_school'),
                                     request.POST.get('p_grade'), request.POST.get('p_birth'), errors, False)
        if person:
            participants.append(person)

    columns = [request.POST.getlist(k) for k in ('f_name', 'f_school', 'f_grade', 'f_birth')]
    for index in range(max(len(c) for c in columns)):
        row = [(c[index] if index < len(c) else '') for c in columns]
        if not any(v.strip() for v in row):
            continue   # 비어 있는 친구 칸은 무시
        person = _person_from_fields(f'친구 {index + 1}', *row, errors, True)
        if person:
            participants.append(person)

    if len(participants) > MAX_PARTICIPANTS:
        errors.append(f'한 번에 최대 {MAX_PARTICIPANTS}명까지 신청할 수 있어요.')
    return participants, errors


# ---------------------------------------------------------------- 공개 화면
def special_lecture_list(request):
    now = timezone.now()
    lectures = SpecialLecture.objects.filter(is_active=True)
    upcoming = [l for l in lectures.filter(lecture_at__gte=now).order_by('lecture_at')]
    past = list(lectures.filter(lecture_at__lt=now).order_by('-lecture_at')[:6])
    return render(request, 'arcade/special/list.html', {
        'upcoming': upcoming, 'past': past,
        'coupon': available_coupon(request.user),
    })


def _lecture_or_404(pk):
    lecture = get_object_or_404(SpecialLecture, pk=pk)
    if not lecture.is_active:
        raise Http404
    return lecture


def special_lecture_detail(request, pk):
    lecture = _lecture_or_404(pk)
    user = request.user
    profile = getattr(user, 'profile', None) if user.is_authenticated else None
    medulab_parent = is_medulab_parent(user)
    context = {
        'lecture': lecture,
        'medulab_parent': medulab_parent,
        'children_options': parent_children_options(user) if medulab_parent else [],
        'coupon': available_coupon(user),
        'example_images': list(lecture.images.all()),
        'form_token': make_form_token(),
        'waitlist_mode': lecture.accepts_applications and lecture.is_full,
        'friend_price': max(lecture.base_price - lecture.friend_discount, 0),
        'prefill': {
            'name': (profile.real_name if profile else '') or '',
            'phone': (profile.phone_number if profile else '') or '',
            'email': (user.email if user.is_authenticated else '') or '',
        },
        'form_data': request.session.pop('special_form_data', None),
    }
    return render(request, 'arcade/special/detail.html', context)


@require_POST
def special_lecture_apply(request, pk):
    lecture = _lecture_or_404(pk)
    user = request.user
    back = redirect('special_lecture_detail', pk=lecture.pk)

    if not lecture.accepts_applications:
        messages.error(request, '지금은 예약 신청을 받지 않는 특강이에요. (모집 기간이 아니에요)')
        return back
    spam = _spam_error(request)
    if spam:
        messages.error(request, spam)
        return back
    waitlist = lecture.is_full   # 정원이 찼으면 '대기 신청'으로 받는다

    participants, errors = _read_participants(request, lecture, user)
    applicant_name = (request.POST.get('applicant_name') or '').strip()[:50]
    phone = _clean_phone(request.POST.get('phone'))
    email = (request.POST.get('email') or '').strip()[:100]
    referral_friend = (request.POST.get('referral_friend') or '').strip()[:50]
    if referral_friend and not is_medulab_student_name(referral_friend):
        errors.append('입력하신 친구가 메듀랩 재원생으로 확인되지 않았어요. 확인 후 다시 입력해 주세요. (할인을 받지 않으려면 칸을 비워 주세요)')
    if not applicant_name:
        errors.append('신청자(보호자) 이름을 입력해 주세요.')
    if not phone:
        errors.append('연락처를 숫자 9~11자리로 입력해 주세요.')
    if email and not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        errors.append('이메일 형식이 올바르지 않아요. 비워 두셔도 돼요.')
    if not request.POST.get('privacy'):
        errors.append('개인정보 수집·이용에 동의해 주세요.')

    if not errors:
        duplicated = _already_applied(lecture, participants)
        if duplicated:
            errors.append(f'이미 신청된 학생이에요: {", ".join(duplicated)}. 결제를 마치지 못했다면 화면 위쪽 "예약 조회"에서 이어서 결제하거나, 30분 뒤 다시 신청해 주세요.')
    if not errors and not waitlist:
        left = lecture.seats_left()
        if left is not None and len(participants) > left:
            errors.append(f'남은 자리가 {left}자리예요. 인원을 줄여서 다시 신청해 주세요.')

    if errors:
        for error in errors:
            messages.error(request, error)
        request.session['special_form_data'] = {k: request.POST.get(k, '') for k in ('applicant_name', 'phone', 'email', 'p_name', 'p_school', 'p_grade', 'p_birth', 'referral_friend')}
        return back

    now = timezone.now()
    with transaction.atomic():
        coupon = available_coupon(user) if request.POST.get('use_coupon') else None
        rows, total, discount, coupon_used = compute_pricing(lecture, participants, coupon, referral=bool(referral_friend))
        if waitlist:
            status = SpecialLectureReservation.STATUS_WAITLIST
        elif total == 0:
            status = SpecialLectureReservation.STATUS_CONFIRMED
        else:
            status = SpecialLectureReservation.STATUS_PENDING
        reservation = SpecialLectureReservation.objects.create(
            lecture=lecture, applicant=user if user.is_authenticated else None,
            applicant_name=applicant_name, phone=phone, email=email, referral_friend=referral_friend,
            amount=total, discount=discount, status=status, privacy_agreed_at=now,
            paid_at=now if status == SpecialLectureReservation.STATUS_CONFIRMED else None,
        )
        for p, row in zip(participants, rows):
            SpecialLectureParticipant.objects.create(
                reservation=reservation, name=p['name'], school=p['school'], grade=p['grade'], birth_date=p['birth_date'], student_id=p['student_id'],
                is_friend=p['is_friend'], price=row['price'], note=row['note'],
            )
        if coupon_used:
            coupon.reservation = reservation
            if status == SpecialLectureReservation.STATUS_CONFIRMED:
                coupon.used_at = now
            coupon.save(update_fields=['reservation', 'used_at'])
    _count_application(request)

    if waitlist:
        notify_admin(reservation, '대기 신청')
        messages.success(request, '대기 신청이 접수되었어요. 자리가 나면 연락드릴게요.')
        return redirect('special_reservation', token=reservation.token)
    if status == SpecialLectureReservation.STATUS_CONFIRMED:
        notify_confirmed(reservation)
        messages.success(request, '예약이 확정되었어요!')
        return redirect('special_reservation', token=reservation.token)
    return redirect('special_checkout', token=reservation.token)


def special_lookup(request):
    """연락처 + 신청자 이름으로 내 예약을 찾아 예약 확인/결제 화면으로 이동 (비회원용)"""
    found, searched = [], False
    if request.method == 'POST':
        searched = True
        key = f'special_lookup_{_client_ip(request)}'
        if cache.get(key, 0) >= 15:
            messages.error(request, '조회가 너무 많아요. 잠시 뒤 다시 시도해 주세요.')
        else:
            cache.set(key, cache.get(key, 0) + 1, 600)
            phone = _clean_phone(request.POST.get('phone'))
            name = (request.POST.get('applicant_name') or '').strip()
            if phone and name:
                found = list(SpecialLectureReservation.objects.select_related('lecture')
                             .filter(phone=phone, applicant_name=name).order_by('-created_at')[:20])
    return render(request, 'arcade/special/lookup.html', {'found': found, 'searched': searched})


def _reservation_or_404(token):
    return get_object_or_404(SpecialLectureReservation.objects.select_related('lecture'), token=token)


def special_reservation(request, token):
    reservation = _reservation_or_404(token)
    return render(request, 'arcade/special/reservation.html', {
        'reservation': reservation, 'participants': reservation.participants.all(),
        'lecture': reservation.lecture,
    })


def _portone_customer(reservation):
    from .views import portone_email

    if reservation.applicant_id:
        email = portone_email(reservation.applicant)
    elif re.fullmatch(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', reservation.email or ''):
        email = reservation.email
    else:
        email = f'special{reservation.id}@medulab.kr'
    return {
        'portone_store_id': settings.PORTONE_STORE_ID,
        'portone_channel_key_card': settings.PORTONE_CHANNEL_KEY_CARD,
        'portone_channel_key_kakaopay': settings.PORTONE_CHANNEL_KEY_KAKAOPAY,
        'portone_customer_email': email,
        'portone_customer_phone': reservation.phone or '01000000000',
        'portone_customer_name': reservation.applicant_name,
    }


def special_checkout(request, token):
    reservation = _reservation_or_404(token)
    if reservation.status != SpecialLectureReservation.STATUS_PENDING:
        return redirect('special_reservation', token=reservation.token)
    return render(request, 'arcade/special/checkout.html', {
        'reservation': reservation, 'participants': reservation.participants.all(),
        'lecture': reservation.lecture, 'expired': reservation.is_expired_pending, **_portone_customer(reservation),
    })


@require_POST
def special_verify(request, token):
    """결제창 완료 후 서버가 포트원 API로 실제 결제 상태와 금액을 다시 확인하고 예약을 확정한다"""
    import requests

    from .views import _portone_method_label, _portone_not_paid_response

    reservation = _reservation_or_404(token)
    if reservation.status == SpecialLectureReservation.STATUS_CONFIRMED:
        return JsonResponse({'ok': True, 'already_paid': True})
    if reservation.status == SpecialLectureReservation.STATUS_CANCELED:
        return JsonResponse({'ok': False, 'error': '취소된 예약입니다.'}, status=400)
    if not settings.PORTONE_API_SECRET:
        return JsonResponse({'ok': False, 'error': '결제 연동이 아직 설정되지 않았습니다.'}, status=503)

    try:
        resp = requests.get(
            f'https://api.portone.io/payments/{reservation.portone_payment_id}',
            headers={'Authorization': f'PortOne {settings.PORTONE_API_SECRET}'}, timeout=10,
        )
    except requests.RequestException:
        return JsonResponse({'ok': False, 'error': '결제 확인 중 오류가 발생했습니다.', 'retry': True}, status=502)
    if resp.status_code != 200:
        return JsonResponse({'ok': False, 'error': '결제 정보를 확인할 수 없습니다.', 'retry': True}, status=502)

    data = resp.json()
    if data.get('status') != 'PAID':
        return _portone_not_paid_response(data.get('status'))
    if (data.get('amount') or {}).get('total') != reservation.amount:
        return JsonResponse({'ok': False, 'error': '결제 금액이 신청 금액과 일치하지 않습니다.'}, status=400)

    lecture = reservation.lecture
    if lecture.capacity and _live_participants(lecture, exclude_reservation=reservation).count() + reservation.participants.count() > lecture.capacity:
        # 결제하는 사이 정원이 찼다: 자동 환불하고 예약은 취소한다
        refunded, detail = refund_reservation(reservation, '정원 초과 자동 환불')
        if refunded:
            reservation.status = SpecialLectureReservation.STATUS_CANCELED
            reservation.memo = '정원 초과로 자동 환불·취소'
            reservation.save(update_fields=['status', 'memo'])
            reservation.coupons.filter(used_at__isnull=True).update(reservation=None)
            return JsonResponse({'ok': False, 'error': '결제하시는 사이 정원이 마감되어 결제가 자동으로 취소(환불)되었어요. 죄송합니다.'}, status=409)
        reservation.memo = f'정원 초과 + 자동 환불 실패(수동 환불 필요): {detail}'[:200]
        reservation.save(update_fields=['memo'])
        notify_admin(reservation, '정원 초과 · 환불 필요')
        return JsonResponse({'ok': False, 'error': '결제하시는 사이 정원이 마감되었어요. 학원에서 바로 환불해 드릴게요. 학원으로 문의해 주세요.'}, status=409)

    with transaction.atomic():
        reservation.status = SpecialLectureReservation.STATUS_CONFIRMED
        reservation.paid_at = timezone.now()
        reservation.portone_pay_method = _portone_method_label(data.get('method'))
        reservation.save(update_fields=['status', 'paid_at', 'portone_pay_method'])
        reservation.coupons.filter(used_at__isnull=True).update(used_at=timezone.now())
    notify_confirmed(reservation)
    return JsonResponse({'ok': True})


# ---------------------------------------------------------------- 관리자 화면
def _staff(user):
    return user.is_staff


@login_required
@user_passes_test(_staff)
def special_admin_list(request):
    from django.contrib.auth.models import User

    lectures = list(SpecialLecture.objects.all())
    selected = None
    lecture_id = request.GET.get('lecture')
    if lecture_id and lecture_id.isdigit():
        selected = next((l for l in lectures if l.id == int(lecture_id)), None)
    elif lectures:
        selected = lectures[0]
    reservations = []
    if selected:
        reservations = list(selected.reservations.prefetch_related('participants').select_related('applicant'))
        for r in reservations:
            r.pay_url = request.build_absolute_uri(reverse('special_checkout', args=[r.token]))
    for lecture in lectures:
        lecture.confirmed_count = SpecialLectureParticipant.objects.filter(
            reservation__lecture=lecture, reservation__status=SpecialLectureReservation.STATUS_CONFIRMED).count()
        lecture.waitlist_total = lecture.waitlist_count()
    eligible = User.objects.filter(is_active=True, profile__onboarding_complete=True).exclude(
        special_coupons__kind=SpecialLectureCoupon.KIND_WELCOME).count()
    return render(request, 'arcade/special/admin_list.html', {
        'lectures': lectures, 'selected': selected, 'reservations': reservations, 'coupon_eligible_count': eligible,
    })


@login_required
@user_passes_test(_staff)
def special_admin_form(request, pk=None):
    from .forms import SpecialLectureForm

    lecture = get_object_or_404(SpecialLecture, pk=pk) if pk else None
    if request.method == 'POST':
        form = SpecialLectureForm(request.POST, request.FILES, instance=lecture)
        if form.is_valid():
            saved = form.save()
            skipped = _save_example_images(request, saved)
            messages.success(request, '특강을 저장했어요.')
            if skipped:
                messages.error(request, f'이미지가 아니거나 8MB가 넘는 파일 {skipped}개는 올리지 못했어요.')
            return redirect(f"{reverse('special_admin_list')}?lecture={saved.pk}")
    else:
        form = SpecialLectureForm(instance=lecture)
    return render(request, 'arcade/special/admin_form.html', {
        'form': form, 'lecture': lecture, 'title': '특강 수정' if lecture else '특강 등록',
        'images': lecture.images.all() if lecture else [],
    })


MAX_IMAGE_BYTES = 8 * 1024 * 1024


def _save_example_images(request, lecture):
    """수업 내용 예시 사진: 선택한 사진 삭제 + 새로 올린 사진 추가. 올리지 못한 파일 수를 돌려준다"""
    from PIL import Image

    delete_ids = [int(i) for i in request.POST.getlist('delete_images') if i.isdigit()]
    if delete_ids:
        for image in lecture.images.filter(pk__in=delete_ids):
            image.image.delete(save=False)
            image.delete()
    skipped = 0
    next_order = (lecture.images.order_by('-order').values_list('order', flat=True).first() or 0) + 1
    for upload in request.FILES.getlist('example_images'):
        try:
            if upload.size > MAX_IMAGE_BYTES:
                raise ValueError('too large')
            Image.open(upload).verify()
            upload.seek(0)
        except Exception:
            skipped += 1
            continue
        SpecialLectureImage.objects.create(lecture=lecture, image=upload, order=next_order)
        next_order += 1
    return skipped


@login_required
@user_passes_test(_staff)
@require_POST
def special_admin_cancel(request, pk):
    """예약 취소. 결제된 건은 포트원에 환불을 요청하고, 환불이 성공해야 취소한다.
    환불 없이 취소(포트원에서 직접 환불)하려면 skip_refund=1"""
    reservation = get_object_or_404(SpecialLectureReservation, pk=pk)
    back = redirect(f"{reverse('special_admin_list')}?lecture={reservation.lecture_id}")
    paid = bool(reservation.paid_at and reservation.amount and not reservation.refunded_at)
    note = ''
    if paid and not request.POST.get('skip_refund'):
        ok, detail = refund_reservation(reservation, '관리자 예약 취소')
        if not ok:
            messages.error(request, f'환불에 실패해서 취소하지 않았어요: {detail} — 포트원 관리자 화면에서 직접 환불한 뒤 "환불 없이 취소"를 눌러 주세요.')
            return back
        note = ' (결제 금액은 포트원으로 환불 요청했어요)'
    elif paid:
        note = ' 결제된 금액은 포트원에서 직접 환불해 주세요.'
    reservation.status = SpecialLectureReservation.STATUS_CANCELED
    reservation.save(update_fields=['status'])
    reservation.coupons.filter(used_at__isnull=False).update(used_at=None)   # 쿠폰 돌려주기
    messages.success(request, f'{reservation.applicant_name} 님의 예약을 취소했어요.{note}')
    return back


@login_required
@user_passes_test(_staff)
@require_POST
def special_admin_promote(request, pk):
    """대기 신청을 승인한다: 무료면 바로 확정, 유료면 결제 대기로 바꾸고(30분간 자리 확보) 결제 링크를 안내한다"""
    reservation = get_object_or_404(SpecialLectureReservation.objects.select_related('lecture'), pk=pk)
    back = redirect(f"{reverse('special_admin_list')}?lecture={reservation.lecture_id}")
    if reservation.status != SpecialLectureReservation.STATUS_WAITLIST:
        messages.info(request, '대기 신청 상태가 아니에요.')
        return back
    left = reservation.lecture.seats_left()
    if left is not None and reservation.participants.count() > left:
        messages.error(request, f'남은 자리가 {left}자리라 승인할 수 없어요. 다른 예약을 취소해 자리를 만든 뒤 다시 시도해 주세요.')
        return back
    now = timezone.now()
    if reservation.amount == 0:
        reservation.status = SpecialLectureReservation.STATUS_CONFIRMED
        reservation.paid_at = now
        reservation.save(update_fields=['status', 'paid_at'])
        reservation.coupons.filter(used_at__isnull=True).update(used_at=now)
        notify_confirmed(reservation)
        messages.success(request, f'{reservation.applicant_name} 님의 예약을 확정했어요.')
    else:
        reservation.status = SpecialLectureReservation.STATUS_PENDING
        reservation.save(update_fields=['status'])
        SpecialLectureReservation.objects.filter(pk=reservation.pk).update(created_at=now)   # 30분 자리 확보 시작
        link = request.build_absolute_uri(reverse('special_checkout', args=[reservation.token]))
        messages.success(request, f'{reservation.applicant_name} 님께 아래 결제 링크를 문자/카톡으로 보내 주세요 (30분간 자리를 잡아 둬요): {link}')
    return back


@login_required
@user_passes_test(_staff)
@require_POST
def special_admin_remind(request, pk):
    """확정된 예약자에게 특강 하루 전 안내 알림톡을 보낸다 (아직 안내하지 않은 건만)"""
    lecture = get_object_or_404(SpecialLecture, pk=pk)
    sent, failed, reasons = send_reminders(lecture)
    if failed:
        messages.error(request, f'안내 알림 {sent}건 발송, {failed}건 실패: {" / ".join(reasons)}')
    elif sent:
        messages.success(request, f'참가 안내 알림톡을 {sent}건 보냈어요.')
    else:
        messages.info(request, '새로 안내할 확정 예약이 없어요. (이미 보냈거나 확정된 예약이 없어요)')
    return redirect(f"{reverse('special_admin_list')}?lecture={lecture.pk}")


@login_required
@user_passes_test(_staff)
@require_POST
def special_admin_grant_coupons(request):
    """가입 선물 쿠폰이 없는 기존 회원 모두에게 특강 무료 쿠폰 1장씩 지급 (한 사람에게 두 번 지급되지 않음)"""
    from django.contrib.auth.models import User

    users = list(User.objects.filter(is_active=True, profile__onboarding_complete=True).exclude(
        special_coupons__kind=SpecialLectureCoupon.KIND_WELCOME))
    SpecialLectureCoupon.objects.bulk_create([SpecialLectureCoupon(user=u) for u in users])
    messages.success(request, f'기존 회원 {len(users)}명에게 특강 무료 쿠폰을 지급했어요.')
    return redirect('special_admin_list')


@login_required
@user_passes_test(_staff)
def special_admin_export(request, pk):
    """신청 내역 CSV (엑셀에서 한글이 깨지지 않도록 BOM 포함)"""
    lecture = get_object_or_404(SpecialLecture, pk=pk)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="special_{lecture.pk}_reservations.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['신청일시', '상태', '신청자', '연락처', '이메일', '참가자', '학교', '학년', '생년월일', '친구', '참가비',
                     '적용 내역', '결제 수단', '결제일시', '메듀랩 친구', '개인정보 동의', '환불', '메모'])
    for r in lecture.reservations.prefetch_related('participants').order_by('created_at'):
        for p in r.participants.all():
            writer.writerow([
                timezone.localtime(r.created_at).strftime('%Y-%m-%d %H:%M'), r.get_status_display(), r.applicant_name, r.phone,
                r.email, p.name, p.school, p.grade, p.birth_date.strftime('%Y-%m-%d') if p.birth_date else '',
                '친구' if p.is_friend else '', p.price, p.note, r.portone_pay_method,
                timezone.localtime(r.paid_at).strftime('%Y-%m-%d %H:%M') if r.paid_at else '', r.referral_friend,
                timezone.localtime(r.privacy_agreed_at).strftime('%Y-%m-%d %H:%M') if r.privacy_agreed_at else '',
                r.refund_detail, r.memo])
    return response


@login_required
@user_passes_test(_staff)
def special_admin_roster(request, pk):
    """특강 당일 출석 체크용 참가자 명단 (확정된 예약만, 인쇄용)"""
    lecture = get_object_or_404(SpecialLecture, pk=pk)
    people = list(SpecialLectureParticipant.objects.filter(
        reservation__lecture=lecture, reservation__status=SpecialLectureReservation.STATUS_CONFIRMED
    ).select_related('reservation').order_by('name'))
    return render(request, 'arcade/special/roster.html', {'lecture': lecture, 'people': people})


@login_required
@user_passes_test(_staff)
@require_POST
def special_admin_delete(request, pk):
    """특강 삭제. 확정·결제 대기 예약이 남아 있으면 기록이 사라지지 않도록 막고, 목록에서 숨기도록 안내한다"""
    lecture = get_object_or_404(SpecialLecture, pk=pk)
    live = lecture.reservations.exclude(status=SpecialLectureReservation.STATUS_CANCELED).count()
    if live:
        messages.error(request, f'"{lecture.title}"에는 예약이 {live}건 있어 삭제할 수 없어요. 예약을 모두 취소하거나, 수정 화면에서 "목록에 노출"을 꺼서 숨겨 주세요.')
        return redirect(f"{reverse('special_admin_list')}?lecture={lecture.pk}")
    title = lecture.title
    lecture.delete()
    messages.success(request, f'"{title}" 특강을 삭제했어요.')
    return redirect('special_lecture_list' if request.POST.get('next') == 'public' else 'special_admin_list')
