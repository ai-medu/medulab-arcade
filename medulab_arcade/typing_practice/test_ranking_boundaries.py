"""Deterministic quarter boundaries and ranking behavior with persisted scores."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from .models import TypingHallOfFame, TypingScore
from .views import (
    build_language_ranking_snapshot,
    get_current_quarter_info,
    update_hall_of_fame_for_language,
)


SEOUL = ZoneInfo("Asia/Seoul")


class QuarterBoundaryTests(SimpleTestCase):
    def test_quarter_rollover_and_leap_day_preserve_timezone(self):
        for instant, key, start, end in (
            (datetime(2028, 2, 29, 12, tzinfo=SEOUL), "2028-Q1", (2028, 1, 1), (2028, 4, 1)),
            (datetime(2026, 3, 31, 23, 59, 59, tzinfo=SEOUL), "2026-Q1", (2026, 1, 1), (2026, 4, 1)),
            (datetime(2026, 4, 1, tzinfo=SEOUL), "2026-Q2", (2026, 4, 1), (2026, 7, 1)),
            (datetime(2026, 7, 1, tzinfo=SEOUL), "2026-Q3", (2026, 7, 1), (2026, 10, 1)),
            (datetime(2026, 12, 31, 23, 59, 59, tzinfo=SEOUL), "2026-Q4", (2026, 10, 1), (2027, 1, 1)),
        ):
            with self.subTest(instant=instant):
                info = get_current_quarter_info(instant)
                self.assertEqual(info["key"], key)
                self.assertEqual(info["start"], datetime(*start, tzinfo=SEOUL))
                self.assertEqual(info["end"], datetime(*end, tzinfo=SEOUL))


class RankingBoundaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(username="ranking-student")
        cls.rival = User.objects.create_user(username="ranking-rival")
        cls.staff = User.objects.create_user(username="ranking-staff", is_staff=True)
        cls.superuser = User.objects.create_user(username="ranking-superuser", is_superuser=True)

    def setUp(self):
        self.quarter = get_current_quarter_info(datetime(2026, 5, 15, 12, tzinfo=SEOUL))

    def add_score(self, user=None, *, at=None, **overrides):
        values = {"practice_type": "word", "language": "ko", "speed": 300, "score": 1000, "accuracy": 95}
        values.update(overrides)
        score = TypingScore.objects.create(user=user or self.student, **values)
        # auto_now_add ignores create-time values, so set the historical instant explicitly.
        TypingScore.objects.filter(pk=score.pk).update(created_at=at or self.quarter["start"])
        return score

    def word_entries(self):
        groups, _, _ = build_language_ranking_snapshot("ko", self.quarter)
        challenge = next(group for group in groups if group["code"] == "challenge")
        return next(section["entries"] for section in challenge["practice_sections"] if section["practice_type"] == "word")

    def test_quarter_start_is_inclusive_and_end_exclusive(self):
        self.add_score(at=self.quarter["start"] - timedelta(microseconds=1), speed=1000)
        self.add_score(at=self.quarter["start"], speed=200, score=600)
        self.add_score(at=self.quarter["end"] - timedelta(microseconds=1), speed=400, score=800)
        self.add_score(at=self.quarter["end"], speed=1200)
        entries = self.word_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["attempts"], 2)
        self.assertEqual(entries[0]["average_speed"], 300)
        self.assertEqual(entries[0]["best_speed"], 400)
        self.assertEqual(entries[0]["total_score"], 1400)

    def test_other_languages_key_practice_and_administrators_are_excluded(self):
        self.add_score(speed=200)
        self.add_score(language="en", speed=1000)
        self.add_score(practice_type="key", speed=1000)
        self.add_score(self.staff, speed=1000)
        self.add_score(self.superuser, speed=1000)
        entries = self.word_entries()
        self.assertEqual([entry["username"] for entry in entries], [self.student.username])
        self.assertEqual(entries[0]["attempts"], 1)
        self.assertEqual(entries[0]["average_speed"], 200)

    def test_average_speed_wins_over_a_single_fast_attempt(self):
        self.add_score(speed=600)
        self.add_score(speed=100)
        self.add_score(self.rival, speed=400)
        entries = self.word_entries()
        self.assertEqual([entry["username"] for entry in entries], [self.rival.username, self.student.username])
        self.assertEqual([entry["average_speed"] for entry in entries], [400, 350])
        self.assertEqual(entries[1]["best_speed"], 600)

    def test_equal_average_prefers_accuracy_then_earlier_achievement(self):
        early = self.quarter["start"]
        self.add_score(at=early, accuracy=95)
        self.add_score(self.rival, at=early + timedelta(days=1), accuracy=96)
        self.assertEqual(self.word_entries()[0]["username"], self.rival.username)
        TypingScore.objects.filter(user=self.student).update(accuracy=96)
        self.assertEqual(self.word_entries()[0]["username"], self.student.username)

    def test_practice_leaderboard_contains_only_top_five(self):
        for index in range(6):
            user = User.objects.create_user(username=f"top-{index}")
            self.add_score(user, speed=100 + index * 10)
        entries = self.word_entries()
        self.assertEqual([entry["username"] for entry in entries], ["top-5", "top-4", "top-3", "top-2", "top-1"])

    def test_empty_quarter_does_not_create_hall_of_fame_records(self):
        self.assertEqual(self.word_entries(), [])
        update_hall_of_fame_for_language("ko", self.quarter)
        self.assertFalse(TypingHallOfFame.objects.exists())

    def test_hall_of_fame_is_idempotent_and_retains_better_historical_record(self):
        self.add_score(speed=500)
        update_hall_of_fame_for_language("ko", self.quarter)
        legend = TypingHallOfFame.objects.get(language="ko", practice_type="word", category="peak_speed")
        record_ids = set(TypingHallOfFame.objects.values_list("pk", flat=True))
        update_hall_of_fame_for_language("ko", self.quarter)
        self.assertSetEqual(set(TypingHallOfFame.objects.values_list("pk", flat=True)), record_ids)

        next_quarter = get_current_quarter_info(self.quarter["end"])
        self.add_score(self.rival, at=next_quarter["start"], speed=400)
        update_hall_of_fame_for_language("ko", next_quarter)
        legend.refresh_from_db()
        self.assertEqual((legend.user, legend.record_value, legend.quarter_key), (self.student, 500, "2026-Q2"))

        self.add_score(self.rival, at=next_quarter["start"], speed=600)
        update_hall_of_fame_for_language("ko", next_quarter)
        legend.refresh_from_db()
        self.assertEqual((legend.user, legend.record_value, legend.quarter_key), (self.rival, 600, "2026-Q3"))
