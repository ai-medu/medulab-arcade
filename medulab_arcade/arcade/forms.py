from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator

from .models import Badge, Project, ScheduleEvent, Tag, UserProfile, Notice, Award, Certification, CertInfo, CompetitionType, Contest, SchoolClass, ConsultInquiry


BADGE_CRITERIA_HELP = (
    '지원 조건: typing_total_count(누적 타자 기록 수), typing_accuracy(정확도 이상), '
    'typing_speed(타속 이상), typing_practice_first(유형별 첫 기록), '
    'program_completion(연결 과정 이수), program_completion_count(서로 다른 과정 이수 수), '
    'homework_completion_count(완료 숙제 수), mission_completion_count(완료 미션 수)'
)



def _check_children_required_fields(form, children):
    """자녀 정보가 입력된 경우 각 자녀의 이름·생년월일은 필수 (학교/학년은 선택)."""
    for idx, child in enumerate(children, start=1):
        if not isinstance(child, dict):
            continue
        missing = [label for key, label in (('name', '이름'), ('birth_date', '생년월일')) if not str(child.get(key) or '').strip()]
        if missing:
            form.add_error(None, f'자녀 {idx}의 {", ".join(missing)}을(를) 입력해 주세요.')



def normalize_children_info(value):
    """UserProfile.children_info 를 항상 [{...}, ...] 형태로 돌려준다.
    과거에 '[]' 같은 문자열(JSON을 한 번 더 감싼 값)로 저장된 데이터도 풀어서 읽는다."""
    import json
    for _ in range(3):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                return []
        else:
            break
    if not isinstance(value, list):
        return []
    return [c for c in value if isinstance(c, dict)]

class ProjectUploadForm(forms.ModelForm):
    tags_str = forms.CharField(
        label='태그(쉼표로 구분)',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': '예: pygame, 액션, 2인용',
                'class': 'form-input',
            }
        ),
        help_text='태그를 쉼표(,)로 구분해 입력해 주세요.',
    )

    class Meta:
        model = Project
        fields = [
            'author',
            'title',
            'description',
            'categories',
            'author_display_name',
            'thumbnail',
            'thumbnail_emoji',
            'color',
            'accent',
            'project_zip',
            'entry_file',
            'external_url',
        ]
        widgets = {
            'categories': forms.CheckboxSelectMultiple(),
            'title': forms.TextInput(
                attrs={'placeholder': '작품 이름을 입력해 주세요.', 'class': 'form-input'}
            ),
            'description': forms.Textarea(
                attrs={'placeholder': '작품 설명을 작성해 주세요.', 'class': 'form-input', 'rows': 8}
            ),
            'external_url': forms.URLInput(
                attrs={'placeholder': 'https://...', 'class': 'form-input'}
            ),
            'author_display_name': forms.TextInput(
                attrs={'placeholder': '예: 김민준 (중2)', 'class': 'form-input'}
            ),
            'thumbnail_emoji': forms.TextInput(
                attrs={'placeholder': '🎮', 'class': 'form-input'}
            ),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color'}),
            'accent': forms.TextInput(attrs={'type': 'color', 'class': 'form-color'}),
            'entry_file': forms.TextInput(
                attrs={'placeholder': 'index.html', 'class': 'form-input'}
            ),
            'project_zip': forms.FileInput(attrs={'accept': '.zip', 'class': 'form-file'}),
            'thumbnail': forms.FileInput(attrs={'accept': 'image/*', 'class': 'form-file'}),
            'author': forms.Select(
                attrs={'class': 'form-input author-select', 'size': '7'}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['author'].queryset = User.objects.all().order_by('-date_joined')
        self.fields['author'].label = '실제 제작 회원'
        self.fields['author'].required = False

        if user and not self.instance.pk and hasattr(user, 'profile'):
            self.fields['author_display_name'].initial = user.profile.display_name

        if self.instance.pk:
            self.fields['tags_str'].initial = ', '.join(
                tag.name for tag in self.instance.tags.all()
            )

        if not self.instance.pk:
            self.fields['description'].initial = (
                "[작품 설명]\n"
                "\n\n"
                "[조작 방법]\n"
                "- 이동: \n"
                "- 공격/점프: \n\n"
                "[시작 후기]\n"
                "게임이나 프로그램을 어떻게 만들었는지 적어 주세요."
            )

    def clean_tags_str(self):
        tags_str = self.cleaned_data.get('tags_str', '')
        if not tags_str:
            return []

        tag_list = list(dict.fromkeys(tag.strip() for tag in tags_str.split(',') if tag.strip()))
        if len(tag_list) > 10:
            raise forms.ValidationError('태그는 최대 10개까지 등록할 수 있습니다.')
        return tag_list

    def clean_project_zip(self):
        uploaded = self.cleaned_data.get('project_zip')
        if uploaded:
            if not uploaded.name.lower().endswith('.zip'):
                raise forms.ValidationError('ZIP 파일만 업로드할 수 있습니다.')
            if uploaded.size > 50 * 1024 * 1024:
                raise forms.ValidationError('파일 크기는 50MB 이하여야 합니다.')
        return uploaded

    def clean(self):
        cleaned_data = super().clean()
        project_zip = cleaned_data.get('project_zip')
        external_url = cleaned_data.get('external_url')

        if not self.instance.project_path and not project_zip and not external_url:
            raise forms.ValidationError(
                '작품 파일(ZIP)을 업로드하거나 외부 링크 URL을 입력해 주세요.'
            )
        return cleaned_data

    def save(self, commit=True):
        project = super().save(commit=commit)
        tag_names = self.cleaned_data.get('tags_str', [])

        if commit:
            self._save_tags(project, tag_names)
        else:
            original_save_m2m = self.save_m2m

            def save_m2m():
                original_save_m2m()
                self._save_tags(project, tag_names)

            self.save_m2m = save_m2m

        return project

    def _save_tags(self, project, tag_names):
        project.tags.clear()
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            project.tags.add(tag)


def signup_extra_fields():
    """모든 회원 가입 폼이 함께 쓰는 가입 경로/가입 사유 칸"""
    from .models import SIGNUP_SOURCE_CHOICES
    choices = [('', '선택해 주세요')] + [(c, c) for c in SIGNUP_SOURCE_CHOICES] + [('other', '직접 입력')]
    return {
        'signup_source': forms.ChoiceField(
            label='가입 경로', required=False, choices=choices,
            widget=forms.Select(attrs={'class': 'form-input'}),
        ),
        'signup_source_other': forms.CharField(
            label='가입 경로 직접 입력', required=False, max_length=100,
            widget=forms.TextInput(attrs={'placeholder': '가입 경로를 직접 입력해 주세요.', 'class': 'form-input'}),
        ),
        'signup_reason': forms.CharField(
            label='가입 사유', required=False,
            widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '가입하시는 이유를 간단히 적어 주세요.', 'class': 'form-input'}),
        ),
    }


PARENT_PHONE_TYPES = ('parent', 'medulab_parent')


def clean_signup_extras(form, cleaned_data):
    """전화번호·가입 경로(직접 입력 포함)·가입 사유 필수 검사 (가입 경로/사유는 메듀랩 학생 제외)"""
    asks_source = cleaned_data.get('user_type') != 'medulab_member'
    source = cleaned_data.get('signup_source') or ''
    if not asks_source:
        cleaned_data['signup_source'] = cleaned_data['signup_reason'] = ''
        source = ''
    if source == 'other':
        source = (cleaned_data.get('signup_source_other') or '').strip()
        if not source:
            form.add_error('signup_source_other', '가입 경로를 직접 입력해 주세요.')
    cleaned_data['signup_source'] = source
    if asks_source and not source and 'signup_source_other' not in form.errors:
        form.add_error('signup_source', '가입 경로를 선택해 주세요.')
    if asks_source and not (cleaned_data.get('signup_reason') or '').strip():
        form.add_error('signup_reason', '가입 사유를 입력해 주세요.')
    if 'phone_number' not in form.errors and not cleaned_data.get('phone_number'):
        is_parent = cleaned_data.get('user_type') in PARENT_PHONE_TYPES
        form.add_error('phone_number', '학부모 전화번호를 입력해 주세요.' if is_parent else '전화번호를 입력해 주세요.')


def apply_signup_extras(profile, cleaned_data):
    profile.signup_source = (cleaned_data.get('signup_source') or '')[:100]
    profile.signup_reason = (cleaned_data.get('signup_reason') or '').strip()


class SignUpForm(UserCreationForm):
    USER_TYPE_CHOICES = UserProfile.PUBLIC_TYPE_CHOICES

    real_name = forms.CharField(
        label='이름',
        widget=forms.TextInput(attrs={'placeholder': '실명을 입력해 주세요.', 'class': 'form-input'}),
    )
    birth_date = forms.CharField(
        label='생년월일',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '예: 1989.01.16', 'class': 'form-input'}),
    )
    phone_number = forms.CharField(
        label='전화번호',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': '숫자만 입력해도 됩니다',
                'class': 'form-input',
                'inputmode': 'numeric',
                'autocomplete': 'tel',
            }
        ),
        help_text='하이픈 없이 숫자만 입력해도 자동으로 정리됩니다.',
    )
    email = forms.EmailField(
        label='이메일',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': '이메일 주소', 'class': 'form-input'}),
    )
    user_type = forms.ChoiceField(
        label='회원 유형',
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'}),
        initial='general',
    )
    address = forms.CharField(
        label='주소',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '주소를 입력해 주세요.', 'class': 'form-input'}),
    )
    children_info = forms.CharField(
        label='자녀 정보 (JSON)',
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = User
        fields = ('real_name', 'birth_date', 'username', 'phone_number', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ID'
        self.fields['username'].validators = [UnicodeUsernameValidator()]
        self.fields['username'].help_text = '한글, 영문, 숫자, @/./+/-/_ 만 사용할 수 있습니다.'
        self.fields.update(signup_extra_fields())
        # 메듀랩 학생은 아이디가 이름+생년월일로 자동 생성되므로 직접 입력하지 않는다
        if self.data.get('user_type') == 'medulab_member':
            self.fields['username'].required = False
        self.fields['username'].widget.attrs.update(
            {
                'placeholder': '한글, 영문, 숫자, @/./+/-/_ 만 사용할 수 있습니다.',
                'class': 'form-input',
                'id': 'id_username_field',
            }
        )
        self.fields['email'].widget.attrs.update(
            {
                'placeholder': '이메일 주소',
                'class': 'form-input',
            }
        )
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update(
                {'class': 'form-input', 'placeholder': '비밀번호'}
            )
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update(
                {'class': 'form-input', 'placeholder': '비밀번호 확인'}
            )
        self.order_fields(
            ['real_name', 'birth_date', 'username', 'phone_number', 'email', 'password1', 'password2', 'user_type',
             'address', 'signup_source', 'signup_source_other', 'signup_reason']
        )

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date', '').strip()
        if not birth_date:
            return None

        import datetime

        for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y%m%d'):
            try:
                return datetime.datetime.strptime(birth_date, fmt).date()
            except ValueError:
                continue
        raise forms.ValidationError('날짜 형식이 올바르지 않습니다. (예: 1989.01.16)')

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('이미 가입된 이메일 주소입니다.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        if not digits:
            return ''
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('전화번호는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        if user_type == 'medulab_member':
            birth = cleaned_data.get('birth_date')
            name = ''.join((cleaned_data.get('real_name') or '').split())
            if name and birth:
                generated = f"{name}{birth.strftime('%Y%m%d')}"
                if User.objects.filter(username__iexact=generated).exists():
                    self.add_error('username', '이미 가입된 학생입니다. 아이디를 잊으셨다면 학원에 문의해 주세요.')
                else:
                    cleaned_data['username'] = generated
                    self.errors.pop('username', None)
            elif not self.errors.get('username'):
                self.add_error('username', '이름과 생년월일을 입력하면 아이디가 자동으로 만들어집니다.')
        clean_signup_extras(self, cleaned_data)
        if user_type == 'medulab_parent' and not (cleaned_data.get('address') or '').strip():
            self.add_error('address', '메듀랩 학부모는 주소를 입력해 주세요.')
        if user_type in PARENT_PHONE_TYPES:
            import json

            raw = cleaned_data.get('children_info') or '[]'
            try:
                children = json.loads(raw)
            except (ValueError, TypeError):
                children = []
            if not children:
                self.add_error(None, '자녀 정보를 1명 이상 입력해 주세요.')
            else:
                _check_children_required_fields(self, children)
            cleaned_data['children_info'] = children
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user_type = self.cleaned_data.get('user_type', 'general')
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.user_type = user_type
            profile.real_name = self.cleaned_data.get('real_name')
            profile.birth_date = self.cleaned_data.get('birth_date')
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.address = self.cleaned_data.get('address', '')
            profile.children_info = self.cleaned_data.get('children_info') or None
            apply_signup_extras(profile, self.cleaned_data)
            profile.is_approved = user_type in UserProfile.AUTO_APPROVE_TYPES
            profile.save()
        return user


class AdminUserForm(forms.ModelForm):
    password = forms.CharField(
        label='비밀번호',
        required=False,
        widget=forms.PasswordInput(
            attrs={'placeholder': '변경 시에만 입력해 주세요.', 'class': 'form-input'}
        ),
        help_text='비밀번호를 변경할 때만 입력하고, 유지하려면 비워 두세요.',
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'is_staff', 'is_active')
        labels = {
            'username': '로그인 아이디',
            'email': '이메일 주소',
            'is_staff': '관리자 권한',
            'is_active': '활성 상태',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class AdminUserProfileForm(forms.ModelForm):
    birth_date = forms.DateField(
        label='생년월일', required=False,
        input_formats=['%Y.%m.%d', '%Y-%m-%d', '%Y%m%d'],
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 2016.03.15'}),
        error_messages={'invalid': '날짜 형식이 올바르지 않습니다. (예: 2016.03.15)'},
    )

    class Meta:
        model = UserProfile
        fields = ('user_type', 'is_approved', 'real_name', 'birth_date', 'phone_number', 'nickname',
                  'address', 'notify_attendance', 'notify_news', 'signup_source', 'signup_reason')
        labels = {
            'signup_source': '가입 경로', 'signup_reason': '가입 사유',
            'user_type': '회원 유형', 'is_approved': '승인 여부', 'real_name': '이름',
            'phone_number': '전화번호', 'nickname': '닉네임(표시 이름)', 'address': '주소',
            'notify_attendance': '출석 알림 수신', 'notify_news': '소식 알림 수신',
        }
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-input'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'real_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'inputmode': 'numeric', 'placeholder': '숫자만 입력해도 됩니다'}),
            'nickname': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.TextInput(attrs={'class': 'form-input'}),
            'signup_source': forms.TextInput(attrs={'class': 'form-input'}),
            'signup_reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'notify_attendance': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'notify_news': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 주소와 알림 수신 설정은 학부모 회원에게만 의미가 있어, 학부모가 아니면 칸을 없앤다
        # (없애지 않으면 화면에 없는 체크박스가 저장 때 '해제'로 덮어써진다)
        if self.instance.pk and self.instance.user_type not in ('parent', 'medulab_parent'):
            for name in ('address', 'notify_attendance', 'notify_news'):
                del self.fields[name]

    def clean_phone_number(self):
        digits = ''.join(ch for ch in (self.cleaned_data.get('phone_number') or '') if ch.isdigit())
        if not digits:
            return ''
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('전화번호는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean(self):
        cleaned_data = super().clean()
        # 메듀랩 학부모는 주소 필수 (주소 칸이 있는 폼에서만 검사한다)
        if (cleaned_data.get('user_type') == 'medulab_parent' and 'address' in self.fields
                and not (cleaned_data.get('address') or '').strip()):
            self.add_error('address', '메듀랩 학부모는 주소를 입력해 주세요.')
        return cleaned_data


class AdminOnboardingForm(forms.Form):
    """관리자가 '추가정보 입력 전' 소셜 가입 계정의 정보를 대신 입력하고 가입을 완료(승인)시키는 폼"""

    user_type = forms.ChoiceField(label='회원 유형', choices=UserProfile.PUBLIC_TYPE_CHOICES)
    real_name = forms.CharField(label='이름', max_length=20)
    birth_date = forms.CharField(label='생년월일')
    email = forms.EmailField(label='이메일')
    phone_number = forms.CharField(label='전화번호')
    address = forms.CharField(label='주소', required=False)
    signup_source = forms.CharField(label='가입 경로', required=False, max_length=100)
    signup_reason = forms.CharField(label='가입 사유', required=False)
    approve = forms.BooleanField(label='승인', required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_birth_date(self):
        import datetime

        raw = (self.cleaned_data.get('birth_date') or '').strip()
        for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y%m%d'):
            try:
                return datetime.datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        raise forms.ValidationError('생년월일 형식이 올바르지 않습니다. (예: 2016.03.15)')

    def clean_phone_number(self):
        digits = ''.join(ch for ch in (self.cleaned_data.get('phone_number') or '') if ch.isdigit())
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('전화번호는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        others = User.objects.filter(email__iexact=email)
        if self.user is not None:
            others = others.exclude(pk=self.user.pk)
        if others.exists():
            raise forms.ValidationError('이미 다른 회원이 사용 중인 이메일 주소입니다.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('user_type') == 'medulab_parent' and not (cleaned_data.get('address') or '').strip():
            self.add_error('address', '메듀랩 학부모는 주소를 입력해 주세요.')
        return cleaned_data


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = (
            'code',
            'name',
            'description',
            'icon',
            'color',
            'category',
            'criteria_type',
            'criteria_value',
            'related_program',
            'is_active',
            'sort_order',
        )
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': 'form-input'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'criteria_type': forms.TextInput(attrs={'class': 'form-input'}),
            'criteria_value': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'related_program': forms.Select(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'sort_order': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['criteria_type'].help_text = BADGE_CRITERIA_HELP
        self.fields['criteria_value'].help_text = '조건 달성 기준값입니다. 예: 정확도 90, 타속 250, 이수 과정 3개.'
        self.fields['related_program'].help_text = 'program_completion 조건일 때 연결할 과정을 선택합니다.'


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='아이디 또는 이메일',
        widget=forms.TextInput(
            attrs={
                'placeholder': '아이디 또는 이메일 주소',
                'class': 'form-input',
                'autofocus': True,
            }
        ),
    )
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(
            attrs={'placeholder': '비밀번호', 'class': 'form-input'}
        ),
    )


class UserProfileUpdateForm(forms.ModelForm):
    # 회원 유형은 관리자만 바꿀 수 있어 이 폼에는 없다 (화면에는 읽기 전용으로만 보여 준다)
    username = forms.CharField(
        label='아이디',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'readonly': 'readonly'}),
    )
    email = forms.EmailField(
        label='이메일 주소',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )
    real_name = forms.CharField(
        label='이름',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
    )
    birth_date = forms.CharField(
        label='생년월일',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 2016.03.15'}),
    )
    phone_number = forms.CharField(
        label='전화번호',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-input',
                'placeholder': '숫자만 입력해도 됩니다',
                'inputmode': 'numeric',
                'autocomplete': 'tel',
            }
        ),
        help_text='하이픈 없이 숫자만 입력해도 자동으로 정리됩니다.',
    )
    nickname = forms.CharField(
        label='닉네임(표시 이름)',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-input', 'placeholder': '작품 등록 때 사용할 기본 이름'}
        ),
        help_text='닉네임이 없으면 이름을 먼저 쓰고, 이름도 없으면 아이디를 사용합니다.',
    )
    address = forms.CharField(
        label='주소',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'}),
    )
    children_info = forms.CharField(
        label='자녀 정보 (JSON)',
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = UserProfile
        fields = (
            'real_name', 'birth_date', 'phone_number', 'nickname',
            'address', 'notify_attendance',
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
        self.fields['username'].disabled = True
        self.fields['real_name'].initial = self.instance.real_name
        self.fields['birth_date'].initial = (
            self.instance.birth_date.strftime('%Y.%m.%d') if self.instance.birth_date else ''
        )
        self.fields['phone_number'].initial = self.instance.phone_number
        self.fields['address'].initial = self.instance.address
        # 주소·자녀 정보·알림 수신 설정은 메듀랩 학부모 화면에만 있다. 화면에 없는 칸이 저장 때 비워지거나
        # '해제'로 덮어써지지 않도록 학부모가 아니면 폼에서 뺀다
        self.has_parent_fields = self.instance.user_type == 'medulab_parent'
        # 자녀 정보는 학부모회원·메듀랩 학부모 모두 수정할 수 있다
        self.has_children_fields = self.instance.user_type in PARENT_PHONE_TYPES
        if not self.has_parent_fields:
            for name in ('address', 'notify_attendance'):
                del self.fields[name]
        if not self.has_children_fields:
            del self.fields['children_info']
        import json as _json
        if self.has_children_fields:
            self.fields['children_info'].initial = _json.dumps(normalize_children_info(self.instance.children_info))

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            return ''
        user = self.instance.user
        if User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            raise forms.ValidationError('이미 다른 회원이 사용 중인 이메일 주소입니다.')
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date', '').strip()
        if not birth_date:
            return None

        import datetime

        for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y%m%d'):
            try:
                return datetime.datetime.strptime(birth_date, fmt).date()
            except ValueError:
                continue
        raise forms.ValidationError('날짜 형식이 올바르지 않습니다. (예: 2016.03.15)')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        if not digits:
            return ''
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('전화번호는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean_address(self):
        address = (self.cleaned_data.get('address') or '').strip()
        if self.has_parent_fields and not address:
            raise forms.ValidationError('메듀랩 학부모는 주소를 입력해 주세요.')
        return address

    def save(self, commit=True):
        import json

        profile = super().save(commit=False)
        user = profile.user

        user.email = self.cleaned_data['email']
        profile.real_name = self.cleaned_data['real_name']
        profile.birth_date = self.cleaned_data['birth_date']
        profile.phone_number = self.cleaned_data['phone_number']
        profile.nickname = self.cleaned_data['nickname']
        if self.has_parent_fields:
            profile.address = self.cleaned_data.get('address', '')
        if self.has_children_fields:
            try:
                profile.children_info = normalize_children_info(self.cleaned_data.get('children_info') or '[]') or None
            except (ValueError, TypeError):
                profile.children_info = None

        if commit:
            user.save(update_fields=['email'])
            profile.save()
        return profile


class MedulabParentUpgradeForm(forms.Form):
    """'학부모회원' -> '메듀랩 학부모' 전환 신청 폼 (주소 + 자녀정보 수집)"""

    address = forms.CharField(
        label='주소',
        widget=forms.TextInput(attrs={'placeholder': '주소를 입력해 주세요.', 'class': 'form-input'}),
    )
    children_info = forms.CharField(
        label='자녀 정보 (JSON)',
        widget=forms.HiddenInput(),
    )

    def clean(self):
        import json

        cleaned_data = super().clean()
        raw = cleaned_data.get('children_info') or '[]'
        try:
            children = json.loads(raw)
        except (ValueError, TypeError):
            children = []
        if not children:
            self.add_error(None, '자녀 정보를 1명 이상 입력해 주세요.')
        else:
            _check_children_required_fields(self, children)
        cleaned_data['children_info'] = children
        return cleaned_data


class SocialOnboardingForm(forms.Form):
    """소셜 로그인 최초 가입자의 추가정보(이름/생년월일/전화번호/회원유형) 입력 폼"""

    USER_TYPE_CHOICES = UserProfile.PUBLIC_TYPE_CHOICES

    real_name = forms.CharField(
        label='이름',
        widget=forms.TextInput(attrs={'placeholder': '실명을 입력해 주세요.', 'class': 'form-input'}),
    )
    birth_date = forms.CharField(
        label='생년월일',
        widget=forms.TextInput(attrs={'placeholder': '예: 1989.01.16', 'class': 'form-input'}),
    )
    phone_number = forms.CharField(
        label='전화번호',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'inputmode': 'numeric'}),
    )
    user_type = forms.ChoiceField(
        label='회원 유형',
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'}),
        initial='general',
    )
    address = forms.CharField(
        label='주소',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '주소를 입력해 주세요.', 'class': 'form-input'}),
    )
    children_info = forms.CharField(
        label='자녀 정보 (JSON)',
        required=False,
        widget=forms.HiddenInput(),
    )

    email = forms.EmailField(
        label='이메일',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )

    def __init__(self, *args, user=None, locked_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields.update(signup_extra_fields())
        # 유형이 정해진 가입 링크로 들어온 경우 그 유형만 선택할 수 있다
        if locked_type:
            self.fields['user_type'].choices = [c for c in self.USER_TYPE_CHOICES if c[0] == locked_type]
            self.fields['user_type'].initial = locked_type

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        others = User.objects.filter(email__iexact=email)
        if self.user is not None:
            others = others.exclude(pk=self.user.pk)
        if others.exists():
            raise forms.ValidationError('이미 가입된 이메일 주소입니다.')
        return email

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date', '').strip()
        import datetime

        for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y%m%d'):
            try:
                return datetime.datetime.strptime(birth_date, fmt).date()
            except ValueError:
                continue
        raise forms.ValidationError('날짜 형식이 올바르지 않습니다. (예: 1989.01.16)')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        if not digits:
            return ''
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('전화번호는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean(self):
        import json

        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        clean_signup_extras(self, cleaned_data)
        if user_type == 'medulab_parent' and not (cleaned_data.get('address') or '').strip():
            self.add_error('address', '메듀랩 학부모는 주소를 입력해 주세요.')
        if user_type in PARENT_PHONE_TYPES:
            raw = cleaned_data.get('children_info') or '[]'
            try:
                children = json.loads(raw)
            except (ValueError, TypeError):
                children = []
            if not children:
                self.add_error(None, '자녀 정보를 1명 이상 입력해 주세요.')
            else:
                _check_children_required_fields(self, children)
            cleaned_data['children_info'] = children
        return cleaned_data


class ScheduleEventForm(forms.ModelForm):
    class Meta:
        model = ScheduleEvent
        fields = ['title', 'description', 'event_type', 'start_date', 'end_date', 'days_of_week', 'start_time', 'end_time', 'external_url', 'image', 'is_active']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'start_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'end_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'description': forms.Textarea(attrs={'rows': 6}),
            'event_type': forms.RadioSelect(attrs={'class': 'event-type-radio'}),
        }
        labels = {
            'title': '일정명',
            'description': '상세 설명',
            'start_date': '시작일시',
            'end_date': '종료일시',
            'start_time': '시작 시간',
            'end_time': '종료 시간',
            'event_type': '일정 유형',
            'external_url': '링크 URL',
            'image': '이미지 (포스터)',
            'is_active': '노출 여부',
        }

    days_of_week = forms.MultipleChoiceField(
        choices=[
            ('1', '월'), ('2', '화'), ('3', '수'), ('4', '목'), ('5', '금'), ('6', '토'), ('0', '일')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'days-checkbox'}),
        label='반복 요일',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        days_of_week = cleaned_data.get('days_of_week')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if event_type == ScheduleEvent.EVENT_TYPE_ACADEMIC:
            if not days_of_week or not start_time or not end_time:
                raise forms.ValidationError("정규수업은 반복 요일, 시작 시간, 종료 시간을 모두 입력해야 합니다.")
            # 리스트를 콤마로 연결된 문자열로 변환
            cleaned_data['days_of_week'] = ','.join(days_of_week)
            # ACADEMIC일 때 날짜는 무시하거나 None 처리
            cleaned_data['start_date'] = None
            cleaned_data['end_date'] = None
        else:
            if not start_date or not end_date:
                raise forms.ValidationError(f"{dict(ScheduleEvent.EVENT_TYPE_CHOICES).get(event_type)} 유형은 시작일시와 종료일시를 모두 입력해야 합니다.")
            cleaned_data['days_of_week'] = ''
            cleaned_data['start_time'] = None
            cleaned_data['end_time'] = None

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.days_of_week:
            self.initial['days_of_week'] = self.instance.days_of_week.split(',')
        help_texts = {
            'is_active': '체크하면 학원 일정 페이지에 노출됩니다.',
            'external_url': '대회 페이지나 관련 자료가 있는 링크를 입력하세요. (선택사항)',
            'image': '대회 포스터나 관련 이미지를 첨부할 수 있습니다. (선택사항)',
        }


class TimetableForm(forms.ModelForm):
    """학원시간표 전용 폼 (정규수업 유형 고정)"""
    days_of_week = forms.MultipleChoiceField(
        choices=[
            ('1', '월'), ('2', '화'), ('3', '수'), ('4', '목'), ('5', '금'), ('6', '토'), ('0', '일')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'days-checkbox'}),
        label='수업 요일',
        required=True,
    )

    class Meta:
        model = ScheduleEvent
        fields = ['title', 'days_of_week', 'start_time', 'end_time', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'end_time': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'title': '수업명',
            'start_time': '시작 시간',
            'end_time': '종료 시간',
            'description': '메모 / 설명',
            'is_active': '시간표 노출 여부',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.days_of_week:
            self.initial['days_of_week'] = self.instance.days_of_week.split(',')

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days_of_week')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if not days:
            raise forms.ValidationError("수업 요일을 하나 이상 선택해주세요.")
        if not start_time or not end_time:
            raise forms.ValidationError("시작 시간과 종료 시간을 모두 입력해주세요.")
        if start_time >= end_time:
            raise forms.ValidationError("종료 시간은 시작 시간보다 늦어야 합니다.")
        cleaned_data['days_of_week'] = ','.join(days)
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.event_type = ScheduleEvent.EVENT_TYPE_ACADEMIC
        instance.start_date = None
        instance.end_date = None
        if commit:
            instance.save()
        return instance


class SchoolClassForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=[
            ('1', '월'), ('2', '화'), ('3', '수'), ('4', '목'), ('5', '금'), ('6', '토'), ('0', '일')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'days-checkbox'}),
        label='수업 요일',
        required=False,
    )

    class Meta:
        model = SchoolClass
        fields = ['name', 'teacher', 'days_of_week', 'duration_minutes', 'start_time', 'regular_fee', 'tuition_fee', 'monthly_sessions', 'description', 'is_active', 'show_on_schedule']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'fi'}),
            'duration_minutes': forms.NumberInput(attrs={'min': 5, 'step': 5, 'class': 'fi', 'id': 'id_duration_minutes'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'fi', 'id': 'id_start_time'}, format='%H:%M'),
            'regular_fee': forms.NumberInput(attrs={'min': 0, 'step': 1000, 'class': 'fi', 'id': 'id_regular_fee'}),
            'tuition_fee': forms.NumberInput(attrs={'min': 0, 'step': 1000, 'class': 'fi', 'id': 'id_tuition_fee'}),
            'monthly_sessions': forms.NumberInput(attrs={'min': 1, 'step': 1, 'class': 'fi', 'id': 'id_monthly_sessions'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'fi'}),
        }
        labels = {
            'name': '수업명',
            'teacher': '담당 강사',
            'duration_minutes': '수업 시간(분)',
            'regular_fee': '정가 (월, 원)',
            'tuition_fee': '할인가 (월, 원)',
            'monthly_sessions': '월 기본 출석 횟수',
            'description': '설명',
            'is_active': '운영 중',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(
            profile__user_type__in=['medulab_staff', 'medulab_teacher']
        ).order_by('username')
        self.fields['teacher'].required = False
        self.fields['teacher'].empty_label = '(미지정)'
        self.fields['teacher'].widget.attrs.update({'class': 'fi'})
        if self.instance and self.instance.days_of_week:
            self.initial['days_of_week'] = self.instance.days_of_week.split(',')

    def clean(self):
        import datetime

        cleaned_data = super().clean()
        days = cleaned_data.get('days_of_week') or []
        cleaned_data['days_of_week'] = ','.join(days)

        start_time = cleaned_data.get('start_time')
        duration_minutes = cleaned_data.get('duration_minutes')
        if start_time and duration_minutes:
            end_dt = datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=duration_minutes)
            cleaned_data['end_time'] = end_dt.time()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.end_time = self.cleaned_data.get('end_time')
        if commit:
            instance.save()
            self._sync_schedule_event(instance)
        return instance

    def _sync_schedule_event(self, instance):
        """'정규수업 일정에 표시' 체크 여부에 따라 ScheduleEvent(정규수업)를 생성/갱신/해제"""
        if instance.show_on_schedule and instance.days_of_week and instance.start_time:
            event = instance.schedule_event
            if event is None:
                event = ScheduleEvent(event_type=ScheduleEvent.EVENT_TYPE_ACADEMIC)
            event.title = instance.name
            event.event_type = ScheduleEvent.EVENT_TYPE_ACADEMIC
            event.days_of_week = instance.days_of_week
            event.start_time = instance.start_time
            event.end_time = instance.end_time
            event.is_active = instance.is_active
            event.save()
            if instance.schedule_event_id != event.id:
                instance.schedule_event = event
                instance.save(update_fields=['schedule_event'])
        elif instance.schedule_event_id:
            event = instance.schedule_event
            instance.schedule_event = None
            instance.save(update_fields=['schedule_event'])
            event.delete()


class ConsultInquiryForm(forms.ModelForm):
    class Meta:
        model = ConsultInquiry
        fields = ['applicant_type', 'name', 'age_or_grade', 'phone_number', 'message']
        widgets = {
            'applicant_type': forms.RadioSelect(attrs={'class': 'applicant-radio'}),
            'name': forms.TextInput(attrs={'class': 'fi', 'placeholder': '이름'}),
            'age_or_grade': forms.TextInput(attrs={'class': 'fi', 'placeholder': '나이 또는 학년 (예: 8세, 초등 3학년)'}),
            'phone_number': forms.TextInput(attrs={'class': 'fi', 'placeholder': '연락처 (예: 010-1234-5678)', 'inputmode': 'numeric'}),
            'message': forms.Textarea(attrs={'class': 'fi', 'rows': 4, 'placeholder': '궁금하신 내용을 남겨주시면 확인 후 연락드리겠습니다. (선택)'}),
        }
        labels = {
            'applicant_type': '신청자 구분', 'name': '이름', 'age_or_grade': '나이 또는 학년',
            'phone_number': '연락처', 'message': '문의 내용',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['age_or_grade'].required = False

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number', '')
        digits = ''.join(ch for ch in phone_number if ch.isdigit())
        if len(digits) < 9 or len(digits) > 11:
            raise forms.ValidationError('연락처는 숫자 기준 9자리에서 11자리로 입력해 주세요.')
        return digits

    def clean(self):
        cleaned = super().clean()
        applicant_type = cleaned.get('applicant_type') or ConsultInquiry.APPLICANT_SELF
        if applicant_type == ConsultInquiry.APPLICANT_SELF and not (cleaned.get('name') or '').strip():
            self.add_error('name', '이름을 입력해 주세요.')
        return cleaned


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_pinned', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '공지 제목', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 10, 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
        }

class AwardForm(forms.ModelForm):
    competition_type_search = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Award
        fields = ['thumbnail', 'student_name', 'competition_year', 'competition_type', 'division', 'award_name', 'organization', 'date_awarded', 'content']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'competition_year': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '예: 2025', 'min': '2000', 'max': '2099', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'competition_type': forms.Select(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: #111827; color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'division': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 초등부, 중등부, SW부문', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'award_name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'organization': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 교육부', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'date_awarded': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['competition_type'].queryset = CompetitionType.objects.all().order_by('order', 'name')
        self.fields['competition_type'].empty_label = '대회종류를 선택하세요'
        self.fields['competition_type'].required = False

    def clean(self):
        cleaned_data = super().clean()
        competition_type = cleaned_data.get('competition_type')
        typed_name = (self.data.get('competition_type_search') or '').strip()
        organization = (cleaned_data.get('organization') or '').strip()

        if competition_type:
            cleaned_data['competition_name'] = competition_type.name
            return cleaned_data

        if not typed_name:
            raise ValidationError('대회종류를 선택하거나 새 대회종류명을 입력해 주세요.')

        existing = CompetitionType.objects.filter(name__iexact=typed_name).order_by('order', 'name').first()
        if existing:
            cleaned_data['competition_type'] = existing
            cleaned_data['competition_name'] = existing.name
            return cleaned_data

        cleaned_data['competition_type'] = CompetitionType.objects.create(
            name=typed_name,
            organization=organization or None,
        )
        cleaned_data['competition_name'] = typed_name
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.competition_type = self.cleaned_data.get('competition_type')
        instance.competition_name = self.cleaned_data.get('competition_name') or instance.competition_name
        if commit:
            instance.save()
        return instance


class CertificationForm(forms.ModelForm):
    _IS = 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'
    _IS_SEL = 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: #111827; color:white; border: 1px solid rgba(255,255,255,0.1);'

    class Meta:
        model = Certification
        fields = ['student_name', 'cert_info', 'grade', 'issuer', 'date_acquired', 'thumbnail', 'content']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'cert_info': forms.Select(attrs={'id': 'id_cert_info', 'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: #111827; color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'grade': forms.TextInput(attrs={'id': 'id_grade', 'class': 'form-input', 'placeholder': '급수를 입력하세요 (예: 3급)', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'issuer': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 대한상공회의소', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'date_acquired': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'content': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cert_info'].queryset = CertInfo.objects.all().order_by('order', 'name')
        self.fields['cert_info'].empty_label = '자격종류를 선택하세요'
        self.fields['cert_info'].required = True
        self.fields['grade'].required = False


class CertInfoForm(forms.ModelForm):
    _IS = 'width:100%; padding: 10px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'

    CATEGORY_CHOICES = [
        ('ai',           'AI'),
        ('block_coding', '블록코딩'),
        ('python',       '파이썬코딩'),
        ('robot',        '로봇'),
        ('doc_work',     '문서작업'),
    ]
    GRADE_CHOICES = [
        ('kids_5_7', '유아·어린이 (5~7세)'),
        ('elem_1_2', '초등 1~2학년'),
        ('elem_3_4', '초등 3~4학년'),
        ('elem_5_6', '초등 5~6학년'),
        ('mid_high', '중·고등'),
        ('adult',    '대학·일반'),
    ]

    categories_multi = forms.MultipleChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='분류 (복수 선택 가능)',
    )
    grades_multi = forms.MultipleChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='대상 학년',
    )

    class Meta:
        model = CertInfo
        fields = ['name', 'display_name', 'issuer', 'description', 'grade_info', 'link', 'thumbnail', 'order', 'is_national_cert']
        widgets = {
            'name':         forms.TextInput(attrs={'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
            'display_name': forms.TextInput(attrs={'placeholder': '예) COS Entry 1~4급', 'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
            'issuer':       forms.TextInput(attrs={'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
            'description':  forms.Textarea(attrs={'rows': 5, 'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
            'grade_info':   forms.HiddenInput(),
            'link':         forms.URLInput(attrs={'placeholder': 'https://...', 'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
            'order':        forms.NumberInput(attrs={'style': 'width:100%; padding:10px; border-radius:8px; background:rgba(255,255,255,0.05); color:white; border:1px solid rgba(255,255,255,0.1);'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['categories_multi'].initial = [
                c.strip() for c in (self.instance.category or '').split(',') if c.strip()
            ]
            self.fields['grades_multi'].initial = [
                g.strip() for g in (self.instance.target_grades or '').split(',') if g.strip()
            ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.category = ','.join(self.cleaned_data.get('categories_multi', []))
        instance.target_grades = ','.join(self.cleaned_data.get('grades_multi', []))
        if commit:
            instance.save()
        return instance


class CompetitionTypeForm(forms.ModelForm):
    class Meta:
        model = CompetitionType
        fields = ['name', 'organization', 'description', 'link', 'thumbnail', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'organization': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'order': forms.NumberInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
        }


class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ['title', 'organizer', 'category', 'target_audience', 'start_date', 'end_date', 'thumbnail', 'link', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'organizer': forms.TextInput(attrs={'class': 'form-input', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: AI, 코딩, 로봇', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'target_audience': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '예: 초등 3~6학년, 청소년 누구나', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...', 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'style': 'width:100%; padding: 10px; margin-bottom: 15px; border-radius:8px; background: rgba(255,255,255,0.05); color:white; border: 1px solid rgba(255,255,255,0.1);'}),
        }

