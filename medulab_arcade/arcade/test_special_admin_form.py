import datetime
import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from arcade.models import SpecialLecture, SpecialLectureImage
from arcade.test_special_lecture import make_lecture, make_member


def png(name='ex.png', color='red'):
    buffer = io.BytesIO()
    Image.new('RGB', (40, 30), color).save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class AdminFormTests(TestCase):
    def setUp(self):
        admin = make_member('adm50')
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        self.data = {'title': '새 특강', 'lecture_at': '2030-01-01T14:00', 'capacity': 10, 'base_price': 20000,
                     'friend_discount': 10000, 'registration_open': 'on', 'is_active': 'on', 'thumb_emoji': '🤖'}

    def test_form_pages_render_with_sections(self):
        res = self.client.get(reverse('special_admin_create'))
        for text in ('1. 기본 정보', '2. 일정 · 장소', '3. 모집 · 참가비', '4. 썸네일', '5. 수업 내용', 'name="example_images"'):
            self.assertContains(res, text)
        lecture = make_lecture(title='수정할 특강')
        res = self.client.get(reverse('special_admin_edit', args=[lecture.pk]))
        self.assertContains(res, 'value="수정할 특강"')
        self.assertContains(res, '공개 화면 보기')

    def test_create_with_example_images_and_show_on_detail(self):
        self.data['description'] = '수업 설명'
        res = self.client.post(reverse('special_admin_create'), dict(self.data, example_images=[png('a.png'), png('b.png', 'blue')]))
        self.assertEqual(res.status_code, 302)
        lecture = SpecialLecture.objects.get(title='새 특강')
        self.assertEqual(lecture.images.count(), 2)
        self.client.logout()
        detail = self.client.get(reverse('special_lecture_detail', args=[lecture.pk]))
        self.assertContains(detail, 'sp-example-gallery')
        self.assertContains(detail, '예시 사진 2')

    def test_images_alone_show_content_section_and_can_be_deleted(self):
        lecture = make_lecture(title='사진만')
        image = SpecialLectureImage.objects.create(lecture=lecture, image=png())
        self.assertContains(self.client.get(reverse('special_lecture_detail', args=[lecture.pk])), '📖 수업 내용')
        self.client.post(reverse('special_admin_edit', args=[lecture.pk]), dict(self.data, delete_images=[image.pk]))
        self.assertEqual(lecture.images.count(), 0)

    def test_non_image_upload_is_skipped(self):
        bad = SimpleUploadedFile('x.png', b'not an image', content_type='image/png')
        res = self.client.post(reverse('special_admin_create'), dict(self.data, example_images=[bad]), follow=True)
        self.assertEqual(SpecialLecture.objects.get(title='새 특강').images.count(), 0)
        self.assertContains(res, '올리지 못했어요')

    def test_validation_error_shows_message(self):
        res = self.client.post(reverse('special_admin_create'), dict(self.data, title=''))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '입력 내용을 확인해 주세요')


class CardAndCouponUITests(TestCase):
    def setUp(self):
        SpecialLecture.objects.all().delete()   # 마이그레이션으로 들어간 11월 특강은 제외
        self.lecture = make_lecture(location='메듀랩 AI로봇코딩학원 (광주 서구 화개중앙로 51, 5층 · 화개초 앞)', capacity=10,
                                    end_time=datetime.time(14, 30))

    def test_list_card_shows_short_location_capacity_and_benefits(self):
        res = self.client.get(reverse('special_lecture_list'))
        self.assertContains(res, '📍 메듀랩 AI로봇코딩학원<')
        self.assertNotContains(res, '5층 · 화개초 앞')
        self.assertContains(res, '정원 10명 · 남은 자리 10')
        self.assertContains(res, '참가비 20,000원')
        self.assertContains(res, '쿠폰 사용 · 👬 친구 할인 가능')

    def test_detail_still_shows_full_address(self):
        self.assertContains(self.client.get(reverse('special_lecture_detail', args=[self.lecture.pk])), '화개중앙로 51')

    def test_coupon_section_for_each_visitor(self):
        url = reverse('special_lecture_detail', args=[self.lecture.pk])
        guest = self.client.get(url)
        self.assertContains(guest, '로그인한 회원')
        self.assertNotContains(guest, 'id="useCoupon"')
        user = make_member('nocoupon')
        self.client.force_login(user)
        self.assertContains(self.client.get(url), '쿠폰이 없어요')
        from arcade.special_lecture import grant_welcome_coupon
        grant_welcome_coupon(user)
        self.assertContains(self.client.get(url), 'id="useCoupon"')
