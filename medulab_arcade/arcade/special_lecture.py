"""특강 프로그램: 모집 공고, 예약 신청(회원/비회원), 결제, 관리자 화면"""
import logging
import re
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import Http404, JsonResponse
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
def _send_confirmation_now(reservation_id):
    """예약 확정 안내 알림톡을 신청자 연락처로 보낸다 (결과는 예약 기록에 남기고, 실패해도 예약에는 영향 없음)"""
    from django.db import close_old_connections

    try:
        res = SpecialLectureReservation.objects.select_related('lecture').get(pk=reservation_id)
        if res.notified_at:
            return
        lecture = res.lecture
        template = settings.SOLAPI_TEMPLATE_SPECIAL
        phone = _normalize_phone(res.phone)
        ok = False
        if not phone:
            detail = '수신 번호가 올바르지 않아 발송하지 않음'
        elif not _is_configured(template):
            detail = '알림톡 설정(특강 템플릿 ID) 미완료로 발송하지 않음'
        else:
            when = timezone.localtime(lecture.lecture_at)
            when_label = f'{when.month}월 {when.day}일({"월화수목금토일"[when.weekday()]}) {when:%H:%M}'
            if lecture.end_time:
                when_label += f'~{lecture.end_time:%H:%M}'
            names = ', '.join(res.participants.values_list('name', flat=True))
            ok, detail = _post_alimtalk(phone, template, {
                '#{신청자}': res.applicant_name,
                '#{특강명}': lecture.title,
                '#{일시}': when_label,
                '#{장소}': lecture.location or '메듀랩',
                '#{참가자}': names,
                '#{결제금액}': f'{res.amount:,}원' if res.amount else '무료',
            })
        res.notify_detail = detail[:300]
        if ok:
            res.notified_at = timezone.now()
        res.save(update_fields=['notified_at', 'notify_detail'])
    except Exception:
        logger.exception('특강 예약 알림톡 처리 중 오류')
    finally:
        close_old_connections()


def notify_confirmed(reservation):
    """예약이 확정되면 카카오 알림톡을 보낸다. 외부 API 대기가 화면 응답을 늦추지 않도록 별도 스레드에서 처리한다."""
    _spawn(_send_confirmation_now, reservation.pk)


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

    if not lecture.is_open:
        messages.error(request, '지금은 예약 신청을 받지 않는 특강이에요. (마감되었거나 모집 기간이 아니에요)')
        return back

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

    if not errors:
        left = lecture.seats_left()
        if left is not None and len(participants) > left:
            errors.append(f'남은 자리가 {left}자리예요. 인원을 줄여서 다시 신청해 주세요.')

    if errors:
        for error in errors:
            messages.error(request, error)
        request.session['special_form_data'] = {k: request.POST.get(k, '') for k in ('applicant_name', 'phone', 'email', 'p_name', 'p_school', 'p_grade', 'p_birth', 'referral_friend')}
        return back

    with transaction.atomic():
        coupon = available_coupon(user) if request.POST.get('use_coupon') else None
        rows, total, discount, coupon_used = compute_pricing(lecture, participants, coupon, referral=bool(referral_friend))
        reservation = SpecialLectureReservation.objects.create(
            lecture=lecture, applicant=user if user.is_authenticated else None,
            applicant_name=applicant_name, phone=phone, email=email, referral_friend=referral_friend,
            amount=total, discount=discount,
            status=SpecialLectureReservation.STATUS_CONFIRMED if total == 0 else SpecialLectureReservation.STATUS_PENDING,
            paid_at=timezone.now() if total == 0 else None,
        )
        for p, row in zip(participants, rows):
            SpecialLectureParticipant.objects.create(
                reservation=reservation, name=p['name'], school=p['school'], grade=p['grade'], birth_date=p['birth_date'], student_id=p['student_id'],
                is_friend=p['is_friend'], price=row['price'], note=row['note'],
            )
        if coupon_used:
            coupon.reservation = reservation
            if total == 0:
                coupon.used_at = timezone.now()
            coupon.save(update_fields=['reservation', 'used_at'])

    if total == 0:
        notify_confirmed(reservation)
        messages.success(request, '예약이 확정되었어요!')
        return redirect('special_reservation', token=reservation.token)
    return redirect('special_checkout', token=reservation.token)


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
    for lecture in lectures:
        lecture.confirmed_count = SpecialLectureParticipant.objects.filter(
            reservation__lecture=lecture, reservation__status=SpecialLectureReservation.STATUS_CONFIRMED).count()
    return render(request, 'arcade/special/admin_list.html', {
        'lectures': lectures, 'selected': selected, 'reservations': reservations,
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
    """예약을 취소한다. 이미 결제된 건의 환불은 포트원 관리자 화면에서 따로 처리해야 한다"""
    reservation = get_object_or_404(SpecialLectureReservation, pk=pk)
    reservation.status = SpecialLectureReservation.STATUS_CANCELED
    reservation.save(update_fields=['status'])
    reservation.coupons.filter(used_at__isnull=False).update(used_at=None)   # 쿠폰 돌려주기
    note = ' 결제 완료 건이라면 포트원에서 환불을 따로 진행해 주세요.' if reservation.paid_at and reservation.amount else ''
    messages.success(request, f'{reservation.applicant_name} 님의 예약을 취소했어요.{note}')
    return redirect(f"{reverse('special_admin_list')}?lecture={reservation.lecture_id}")


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
