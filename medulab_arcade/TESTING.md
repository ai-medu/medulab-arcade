# Initial regression coverage

Use the existing Django test runner; no additional test framework is required.
Run these commands only inside your cloud development environment.

## Environment

From the repository root:

```bash
python3 -m venv ../medulab-test-venv
source ../medulab-test-venv/bin/activate
python -m pip install -r medulab_arcade/requirements.txt
cd medulab_arcade
```

The initial run used Linux, Python 3.12.14, Django 6.1.2 and SQLite.
`requirements.txt` has lower bounds rather than locked versions, so future
installations can resolve different dependency versions. Production PostgreSQL
configuration and deployment are outside this test run.

## Commands

```bash
# Added tests only (25 test methods, with additional boundary subtests)
python manage.py test arcade.test_project_upload typing_practice.test_score_api typing_practice.test_ranking_boundaries --noinput -v 2

# Existing and added tests together
python manage.py test --noinput -v 1

# Django configuration and dependency consistency
python manage.py check
python -m pip check
git diff --check
```

Django creates and destroys an isolated in-memory SQLite test database and applies
the repository migrations automatically. A manual `migrate` against a development
or production database is unnecessary. These added tests do not save uploaded
files or call external AI, translation, payment or social login services.

## Coverage

| File | Behavior |
| --- | --- |
| `arcade/test_project_upload.py` | ZIP/link requirement, review status, editing an extracted project, ZIP suffix and 50 MiB boundary, unique tag limit, replacement of tag relations, deferred form persistence including categories |
| `typing_practice/test_score_api.py` | Anonymous/method rejection, session ownership, persisted score values, speed/score caps including zero, malformed input without writes, isolated and monotonic unlocks, strict boolean unlock flags |
| `typing_practice/test_ranking_boundaries.py` | Quarter rollover and leap day, inclusive start/exclusive end, language/practice/admin filtering, average speed ranking, accuracy/time tie breaks, top five, empty rankings, idempotent and historical hall of fame records |

This is targeted regression coverage, not a line coverage percentage or a full
browser/end-to-end suite. No lint tool or separate build command is configured
in the repository. Django system checks and the full test suite are used instead.

## Verified results

Base: `origin/main` at `9eb7c80a1cc37cfdb0e347abc0970f27876c3e0b`.
Branch: `test/initial-coverage`.

| Check | Result |
| --- | --- |
| Added tests | 25 passed |
| Full suite | 61 executed: 57 passed, 4 failed |
| Unmodified base in a separate cloud worktree, same environment | 36 executed: 32 passed, the same 4 failed |
| `python manage.py check` | No issues |
| `python -m pip check` | No broken requirements |
| `git diff --check` | Passed |

The four baseline failures are in existing `courses.tests`:

- `OlympiadAnswerSubmissionFeedbackTests.test_student_submission_generates_deterministic_feedback`:
  rendered HTML does not contain `feedback-score`.
- `OlympiadAnswerZipManageTests.test_download_answer_zip_template_contains_chapter_problem_folders`:
  expected problem-level README path differs from generated subquestion folders.
- `OlympiadAnswerZipManageTests.test_item_page_shows_example_upload_form_for_staff`:
  rendered HTML does not contain `+ 예시답안 직접 추가`.
- `OlympiadAnswerZipManageTests.test_manage_page_shows_direct_example_upload_button`:
  rendered HTML does not contain the expected direct example upload link.

These failures were reproduced without the added tests. Existing product code,
templates, dependencies and tests were left unchanged. GitHub read access was
verified with `git ls-remote`; write/push access was not tested. No push, merge or
deployment was performed.
