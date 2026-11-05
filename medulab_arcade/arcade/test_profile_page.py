from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class ProfilePageTests(TestCase):
    """상단 메뉴의 이름은 프로필 페이지로 연결되고, 프로필 페이지에는 회원정보와 수정 폼만 나온다"""

    def setUp(self):
        self.user = User.objects.create_user('profuser', password='x', email='p@example.com')
        self.client.force_login(self.user)

    def test_profile_shows_only_member_info_and_form(self):
        res = self.client.get(reverse('profile'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '회원 정보 수정')
        self.assertContains(res, 'name="real_name"')
        for gone in ('배지 컬렉션', '받은 좋아요', '내 작품'):
            self.assertNotContains(res, gone)

    def test_top_menu_name_links_to_profile(self):
        res = self.client.get(reverse('profile'))
        self.assertContains(res, f'href="{reverse("profile")}" class="nav-link">👤')
        self.user.is_staff = True
        self.user.save()
        res = self.client.get(reverse('profile'))
        self.assertContains(res, f'href="{reverse("profile")}" class="nav-link accent-text">👤')

    def test_profile_edit_saves(self):
        res = self.client.post(reverse('profile'), {
            'real_name': '홍길동', 'nickname': '길동', 'birth_date': '', 'phone_number': '01012345678',
            'email': 'p@example.com', 'user_type': self.user.profile.user_type,
        })
        self.assertEqual(res.status_code, 302)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.real_name, '홍길동')


class ProfileEditRulesTests(TestCase):
    """회원 유형은 관리자만 바꾼다 / 화면에 없는 칸은 저장 때 지워지지 않는다"""

    def _post(self, user, **extra):
        self.client.force_login(user)
        data = {'real_name': '홍길동', 'nickname': '', 'birth_date': '', 'phone_number': '01012345678',
                'email': user.email}
        data.update(extra)
        return self.client.post(reverse('profile'), data)

    def test_user_type_cannot_be_changed_by_member(self):
        user = User.objects.create_user('kid1', password='x', email='k@example.com')
        before = user.profile.user_type
        res = self._post(user, user_type='medulab_teacher')
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.user_type, before)

    def test_non_parent_save_keeps_address_and_notify(self):
        user = User.objects.create_user('plain', password='x', email='p2@example.com')
        user.profile.address = '서울시 어딘가'
        user.profile.notify_attendance = True
        user.profile.save()
        self._post(user)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.address, '서울시 어딘가')
        self.assertTrue(user.profile.notify_attendance)

    def test_medulab_parent_saves_address_and_notify(self):
        user = User.objects.create_user('mparent', password='x', email='mp@example.com')
        user.profile.user_type = 'medulab_parent'
        user.profile.save()
        res = self._post(user, address='서울 강남구 테헤란로 1 101호', children_info='[]', notify_attendance='on')
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.address, '서울 강남구 테헤란로 1 101호')
        self.assertTrue(user.profile.notify_attendance)
        self.assertTrue(user.profile.notify_news)   # 프로필 화면에서 숨겼으므로 저장해도 바뀌지 않는다
        self.assertEqual(user.profile.user_type, 'medulab_parent')

    def test_profile_shows_type_read_only_and_address_search(self):
        user = User.objects.create_user('mparent2', password='x', email='mp2@example.com')
        user.profile.user_type = 'medulab_parent'
        user.profile.save()
        self.client.force_login(user)
        res = self.client.get(reverse('profile'))
        self.assertContains(res, '회원 유형은 관리자만 변경할 수 있어요')
        self.assertNotContains(res, 'name="user_type"')
        self.assertContains(res, 'profileAddressBtn')


class WorksGalleryPageTests(TestCase):
    """학생 작품 갤러리는 작품 목록만 있는 별도 페이지이고, 업로드 버튼은 여기에 있다"""

    def test_gallery_page_has_only_works_and_upload_button(self):
        user = User.objects.create_user('uploader', password='x')
        self.client.force_login(user)
        res = self.client.get(reverse('works_gallery'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'MEDULAB WORKS')
        self.assertContains(res, 'class="works-upload-btn"')
        self.assertNotContains(res, '<section class="lp-hero"')
        self.assertNotContains(res, '<div class="works-tab-bar"')

    def test_top_menu_no_longer_has_upload_button(self):
        user = User.objects.create_user('uploader2', password='x')
        self.client.force_login(user)
        res = self.client.get(reverse('profile'))
        self.assertNotContains(res, 'class="nav-link accent">📤 업로드')

    def test_gallery_visible_without_login_and_no_upload_button(self):
        res = self.client.get(reverse('works_gallery'))
        self.assertEqual(res.status_code, 200)
        self.assertNotContains(res, 'class="works-upload-btn"')

    def test_home_still_shows_works_section(self):
        res = self.client.get(reverse('home'))
        self.assertContains(res, 'id="works"')
        self.assertContains(res, '<section class="lp-hero"')


class SignupPreselectTests(TestCase):
    """/signup/?type=medulab_parent 링크는 메듀랩 학부모가 선택된 채로 가입 폼이 펼쳐진다"""

    def test_preselect_medulab_parent(self):
        res = self.client.get(reverse('signup') + '?type=medulab_parent')
        self.assertContains(res, 'value="medulab_parent" checked')
        self.assertContains(res, 'id="regularSignupWrap" style="display:block;')
        self.assertContains(res, 'id="typeGridLocked"')

    def test_default_and_invalid_type(self):
        res = self.client.get(reverse('signup') + '?type=hacker')
        self.assertNotContains(res, 'value="medulab_parent" checked')
        self.assertContains(res, 'id="regularSignupWrap" style="display:none;')


KIDS = '[{"name": "민수", "birth_date": "20160315", "school": "한빛초", "grade": "3"}]'


class SignupFieldsTests(TestCase):
    """가입 경로/사유, 학부모 전화번호 필수, 메듀랩 학생 아이디 자동 생성"""

    BASE = {'real_name': '홍길동', 'birth_date': '2016.03.15', 'phone_number': '01012345678',
            'signup_source': '지인 소개', 'signup_reason': '수업 문의', 'email': 'new@example.com',
            'password1': 'Str0ng!pass9', 'password2': 'Str0ng!pass9'}

    def _post(self, **extra):
        data = dict(self.BASE)
        data.update(extra)
        return self.client.post(reverse('signup'), data)

    def test_source_choice_and_reason_saved(self):
        res = self._post(username='gen1', user_type='general', signup_source='네이버 검색', signup_reason='소개받아서')
        self.assertEqual(res.status_code, 302)
        p = User.objects.get(username='gen1').profile
        self.assertEqual((p.signup_source, p.signup_reason), ('네이버 검색', '소개받아서'))

    def test_source_other_text_saved(self):
        self._post(username='gen2', user_type='general', signup_source='other', signup_source_other='동네 카페')
        self.assertEqual(User.objects.get(username='gen2').profile.signup_source, '동네 카페')

    def test_source_other_requires_text(self):
        res = self._post(username='gen3', user_type='general', signup_source='other')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(username='gen3').exists())

    def test_parent_requires_phone(self):
        res = self._post(username='par1', user_type='parent', phone_number='')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '학부모 전화번호를 입력해 주세요.')
        res = self._post(username='par1', user_type='parent', phone_number='010-1234-5678', children_info=KIDS)
        self.assertEqual(res.status_code, 302)

    def test_medulab_member_username_auto_generated(self):
        res = self._post(username='ignored', user_type='medulab_member')
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='홍길동20160315').exists())
        self.assertFalse(User.objects.filter(username='ignored').exists())

    def test_medulab_member_without_username_field(self):
        res = self._post(user_type='medulab_member')
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(username='홍길동20160315').exists())

    def test_medulab_member_duplicate(self):
        User.objects.create_user('홍길동20160315', password='x')
        res = self._post(user_type='medulab_member')
        self.assertContains(res, '이미 가입된 학생입니다')

    def test_signup_page_username_guide(self):
        res = self.client.get(reverse('signup'))
        self.assertContains(res, 'placeholder="한글, 영문, 숫자, @/./+/-/_ 만 사용할 수 있습니다."')
        self.assertContains(res, 'id="id_signup_source"')

    def test_phone_source_reason_required_for_all(self):
        for field in ('phone_number', 'signup_source', 'signup_reason'):
            res = self._post(username='req1', user_type='general', **{field: ''})
            self.assertEqual(res.status_code, 200, field)
            self.assertFalse(User.objects.filter(username='req1').exists(), field)
        res = self._post(username='req1', user_type='general', phone_number='')
        self.assertContains(res, '전화번호를 입력해 주세요.')

    def test_email_required(self):
        res = self._post(username='mail1', user_type='general', email='')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(username='mail1').exists())

    def test_medulab_member_needs_no_source_or_reason(self):
        res = self._post(user_type='medulab_member', signup_source='', signup_reason='')
        self.assertEqual(res.status_code, 302)
        p = User.objects.get(username='홍길동20160315').profile
        self.assertEqual((p.signup_source, p.signup_reason), ('', ''))

    def test_signup_page_hides_source_for_member_via_js_hook(self):
        res = self.client.get(reverse('signup'))
        self.assertContains(res, 'id="group_signup_source"')

    def test_parent_requires_children_info(self):
        res = self._post(username='par2', user_type='parent', children_info='[]')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '자녀 정보를 1명 이상 입력해 주세요.')
        self.assertFalse(User.objects.filter(username='par2').exists())
        res = self._post(username='par2', user_type='parent', children_info=KIDS)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(User.objects.get(username='par2').profile.children_info[0]['name'], '민수')


class SocialOnboardingFieldsTests(TestCase):
    """구글/카카오 가입 후 추가정보 화면도 같은 정보를 받는다"""

    def setUp(self):
        self.user = User.objects.create_user('sociala', password='x', email='')
        self.user.profile.onboarding_complete = False
        self.user.profile.save()
        self.client.force_login(self.user)

    def _data(self, **extra):
        data = {'real_name': '김소셜', 'birth_date': '1990.01.02', 'phone_number': '01011112222',
                'email': 'social@example.com', 'user_type': 'general',
                'signup_source': '블로그', 'signup_reason': '후기를 보고'}
        data.update(extra)
        return data

    def test_page_shows_fields(self):
        res = self.client.get(reverse('social_onboarding'))
        for name in ('name="email"', 'name="phone_number"', 'name="signup_source"', 'name="signup_reason"'):
            self.assertContains(res, name)

    def test_saves_all_info(self):
        res = self.client.post(reverse('social_onboarding'), self._data())
        self.assertEqual(res.status_code, 302)
        self.user.refresh_from_db()
        p = self.user.profile
        self.assertEqual(self.user.email, 'social@example.com')
        self.assertEqual((p.signup_source, p.signup_reason, p.phone_number), ('블로그', '후기를 보고', '01011112222'))
        self.assertTrue(p.onboarding_complete)

    def test_required_fields(self):
        for field in ('email', 'phone_number', 'signup_source', 'signup_reason'):
            res = self.client.post(reverse('social_onboarding'), self._data(**{field: ''}))
            self.assertEqual(res.status_code, 200, field)
        res = self.client.post(reverse('social_onboarding'), self._data(user_type='medulab_member', signup_source='', signup_reason=''))
        self.assertEqual(res.status_code, 302)


class ParentChildrenEditTests(TestCase):
    """학부모회원도 마이페이지에서 자녀 정보를 수정할 수 있다"""

    def test_parent_edits_children(self):
        user = User.objects.create_user('mom2', password='x', email='m2@example.com')
        user.profile.user_type = 'parent'
        user.profile.address = '유지될 주소'
        user.profile.save()
        self.client.force_login(user)
        res = self.client.get(reverse('profile'))
        self.assertContains(res, 'id="profileChildRows"')
        self.assertNotContains(res, 'id="profileAddressBtn"')
        kids = '[{"name": "지우", "birth_date": "20150101", "school": "해솔초", "grade": "4"}]'
        res = self.client.post(reverse('profile'), {'real_name': '엄마', 'nickname': '', 'birth_date': '',
                                                  'phone_number': '01012345678', 'email': 'm2@example.com',
                                                  'children_info': kids})
        self.assertEqual(res.status_code, 302)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.children_info[0]['name'], '지우')
        self.assertEqual(user.profile.address, '유지될 주소')


class AdminLinkChildAddsInfoTests(TestCase):
    """관리자가 검색해서 학생 계정을 연결하면 자녀 정보 행도 함께 생겨 매칭된 자녀로 보인다"""

    def test_link_adds_child_info_row_and_matches(self):
        import datetime
        admin = User.objects.create_user('adm', password='x', is_staff=True)
        parent = User.objects.create_user('mom3', password='x')
        parent.profile.user_type = 'parent'
        parent.profile.save()
        kid = User.objects.create_user('kid20130903', password='x')
        kid.profile.real_name = '정해준'
        kid.profile.birth_date = datetime.date(2013, 9, 3)
        kid.profile.save()
        self.client.force_login(admin)
        url = reverse('member_link_child', args=[parent.id])
        self.client.post(url, {'child_id': kid.id})
        self.client.post(url, {'child_id': kid.id})   # 두 번 눌러도 행이 늘지 않는다
        parent.profile.refresh_from_db()
        self.assertEqual(len(parent.profile.children_info), 1)
        self.assertEqual(parent.profile.children_info[0]['name'], '정해준')
        self.assertEqual(parent.profile.children_info[0]['birth_date'], '20130903')
        res = self.client.get(reverse('member_edit', args=[parent.id]))
        self.assertNotContains(res, '그 외 연결된 자녀 계정')


class AdminListOnboardingBadgeTests(TestCase):
    def test_incomplete_social_signup_is_labelled(self):
        admin = User.objects.create_user('adm9', password='x', is_staff=True)
        ghost = User.objects.create_user('ghost1', password='x', email='g@example.com')
        ghost.profile.onboarding_complete = False
        ghost.profile.save()
        self.client.force_login(admin)
        res = self.client.get(reverse('member_list'))
        self.assertContains(res, '추가정보 입력 전')
