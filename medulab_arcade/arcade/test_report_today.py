from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from typing_practice.models import TypingScore


class ReportTodayLearningTests(TestCase):
    def setUp(self):
        self.kid = User.objects.create_user('kid', password='x')
        profile = self.kid.profile
        profile.user_type, profile.is_approved = 'medulab_member', True   # 마이 리포트는 메듀랩 회원에게 보인다
        profile.save()
        self.client.force_login(self.kid)

    def _score(self, practice, lang, speed, accuracy, user=None):
        return TypingScore.objects.create(user=user or self.kid, practice_type=practice, language=lang,
                                          speed=speed, accuracy=accuracy, score=speed)

    def test_empty_day_shows_guide(self):
        res = self.client.get(reverse('my_report'))
        self.assertContains(res, '오늘의 학습 내용')
        self.assertContains(res, '오늘 학습한 내용이 아직 없습니다')
        self.assertContains(res, 'href="/typing/"')

    def test_today_typing_is_grouped_by_language_and_type(self):
        self._score('short', 'ko', 120, 90)
        self._score('short', 'ko', 180, 95)
        self._score('word', 'en', 60, 88)
        old = self._score('long', 'ko', 500, 100)
        TypingScore.objects.filter(pk=old.pk).update(created_at=timezone.now() - timedelta(days=2))
        self._score('long', 'ko', 400, 100, user=User.objects.create_user('other', password='x'))

        res = self.client.get(reverse('my_report'))
        rows = {(r['language'], r['name']): r for r in res.context['typing_today']}
        self.assertEqual(set(rows), {('한국어', '짧은글연습'), ('영어', '단어연습')})
        self.assertEqual((rows[('한국어', '짧은글연습')]['count'], rows[('한국어', '짧은글연습')]['best'],
                          rows[('한국어', '짧은글연습')]['accuracy']), (2, 180, 92.5))
        self.assertContains(res, '2회 · 최고 180타 · 정확도 92.5%')
        self.assertNotContains(res, '오늘 학습한 내용이 아직 없습니다')
