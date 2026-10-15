"""Exercise score persistence through the real HTTP endpoint and test database."""

from django.contrib.auth.models import User
from django.test import TestCase

from .models import TypingHallOfFame, TypingScore, TypingUnlockProgress


class SaveScoreAPITests(TestCase):
    endpoint = "/typing/api/save-score/"

    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username="score-student")
        cls.other = User.objects.create_user(username="other-student")

    def setUp(self):
        self.client.force_login(self.student)

    def post_score(self, **overrides):
        data = {"type": "word", "lang": "ko", "score": 2400, "speed": 300, "accuracy": 97.5}
        data.update(overrides)
        return self.client.post(self.endpoint, data=data, content_type="application/json")

    def test_anonymous_submission_does_not_create_records_or_unlocks(self):
        self.client.logout()
        response = self.post_score(unlocks={"word_unlocked": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "not_saved")
        self.assertFalse(TypingScore.objects.exists())
        self.assertFalse(TypingUnlockProgress.objects.exists())
        self.assertFalse(TypingHallOfFame.objects.exists())

    def test_get_is_rejected_without_writing_a_score(self):
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(TypingScore.objects.exists())

    def test_record_belongs_to_session_user_and_preserves_valid_values(self):
        response = self.post_score(user_id=self.other.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")
        score = TypingScore.objects.get()
        self.assertEqual(score.user, self.student)
        self.assertEqual((score.practice_type, score.language), ("word", "ko"))
        self.assertEqual((score.score, score.speed, score.accuracy), (2400, 300, 97.5))
        self.assertEqual(
            TypingHallOfFame.objects.get(language="ko", practice_type="word", category="peak_speed").user,
            self.student,
        )

    def test_speed_and_score_caps_at_and_beyond_the_boundary(self):
        for speed, score, expected in (
            (1500, 15000, (1500, 15000)),
            (1501, 15001, (1500, 15000)),
            (300, 99999, (300, 3000)),
            (0, 100, (0, 0)),
        ):
            with self.subTest(speed=speed, score=score):
                response = self.post_score(speed=speed, score=score)
                self.assertEqual(response.status_code, 200, response.content)
                saved = TypingScore.objects.latest("pk")
                self.assertEqual((saved.speed, saved.score), expected)

    def test_invalid_json_and_non_numeric_values_do_not_partially_save(self):
        response = self.client.post(self.endpoint, data="{broken", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")
        for field in ("speed", "score"):
            with self.subTest(field=field):
                response = self.post_score(**{field: "not-a-number"})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["status"], "error")
        self.assertFalse(TypingScore.objects.exists())
        self.assertFalse(TypingUnlockProgress.objects.exists())
        self.assertFalse(TypingHallOfFame.objects.exists())

    def test_unlocks_are_isolated_by_user_and_language_and_cannot_be_revoked(self):
        other_progress = TypingUnlockProgress.objects.create(user=self.other, language="ko")
        response = self.post_score(unlocks={
            "key_levels": ["top", "home", "top", "unknown"], "word_unlocked": True,
        })
        self.assertEqual(response.status_code, 200)
        response = self.post_score(lang="en", unlocks={"short_unlocked": True})
        self.assertEqual(response.status_code, 200)
        response = self.post_score(unlocks={"key_levels": [], "word_unlocked": False})
        self.assertEqual(response.status_code, 200)
        korean = TypingUnlockProgress.objects.get(user=self.student, language="ko")
        english = TypingUnlockProgress.objects.get(user=self.student, language="en")
        self.assertEqual(korean.key_levels, ["home", "top"])
        self.assertTrue(korean.word_unlocked)
        self.assertFalse(korean.short_unlocked)
        self.assertEqual(english.key_levels, ["home"])
        self.assertFalse(english.word_unlocked)
        self.assertTrue(english.short_unlocked)
        other_progress.refresh_from_db()
        self.assertFalse(other_progress.word_unlocked)
        self.assertFalse(other_progress.short_unlocked)

    def test_non_boolean_unlock_values_cannot_grant_access(self):
        response = self.post_score(unlocks={
            "key_levels": "all", "word_unlocked": "true",
            "short_unlocked": 1, "long_unlocked": "false",
        })
        self.assertEqual(response.status_code, 200)
        progress = TypingUnlockProgress.objects.get(user=self.student, language="ko")
        self.assertEqual(progress.key_levels, ["home"])
        self.assertEqual((progress.word_unlocked, progress.short_unlocked, progress.long_unlocked), (False, False, False))
