"""Regression coverage for the public project submission form contract."""

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import ProjectUploadForm
from .models import Category, Project, Tag


class ProjectUploadFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="project-author")

    def make_form(self, *, files=None, instance=None, **overrides):
        data = {
            "author": self.author.pk,
            "title": "My first game",
            "description": "Use the arrow keys to collect stars.",
            "author_display_name": "Student",
            "thumbnail_emoji": "🎮",
            "color": "#1a1a2e",
            "accent": "#e94560",
            "entry_file": "index.html",
            "external_url": "https://example.com/game/",
        }
        data.update(overrides)
        return ProjectUploadForm(data=data, files=files, instance=instance)

    def test_new_project_requires_a_zip_or_external_url(self):
        form = self.make_form(external_url="")
        self.assertFalse(form.is_valid())
        self.assertIn("작품 파일(ZIP)", str(form.non_field_errors()))
        self.assertFalse(Project.objects.exists())

    def test_external_url_submission_is_saved_pending_review(self):
        form = self.make_form()
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()
        project.refresh_from_db()
        self.assertEqual(project.author, self.author)
        self.assertEqual(project.external_url, "https://example.com/game/")
        self.assertEqual(project.status, "pending")
        self.assertFalse(project.project_zip)

    def test_existing_extracted_project_can_be_edited_without_reupload(self):
        project = Project.objects.create(
            author=self.author, title="Old title", description="Old description",
            author_display_name="Student", project_path="projects/already-uploaded",
        )
        # Editing views load persisted FileField values rather than a new instance.
        project.refresh_from_db()
        form = self.make_form(instance=project, external_url="", title="Updated title")
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        project.refresh_from_db()
        self.assertEqual(project.title, "Updated title")
        self.assertEqual(project.project_path, "projects/already-uploaded")

    def test_zip_extension_is_case_insensitive(self):
        form = self.make_form(
            external_url="",
            files={"project_zip": SimpleUploadedFile("game.ZIP", b"zip fixture")},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_non_zip_upload_is_rejected_even_with_valid_external_url(self):
        form = self.make_form(
            files={"project_zip": SimpleUploadedFile("game.exe", b"executable")},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("ZIP 파일만", str(form.errors["project_zip"]))

    def test_zip_size_limit_includes_exactly_50_mib(self):
        # Form validation reads upload metadata; no 50 MiB allocation is needed.
        for size, valid in ((50 * 1024 * 1024, True), (50 * 1024 * 1024 + 1, False)):
            with self.subTest(size=size):
                upload = SimpleUploadedFile("game.zip", b"zip fixture")
                upload.size = size
                form = self.make_form(files={"project_zip": upload})
                self.assertEqual(form.is_valid(), valid, form.errors)
                if not valid:
                    self.assertIn("50MB", str(form.errors["project_zip"]))

    def test_tags_are_trimmed_deduplicated_and_empty_entries_ignored(self):
        form = self.make_form(tags_str=" pygame, ,액션,pygame, 액션 , puzzle,")
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save()
        self.assertSetEqual(set(project.tags.values_list("name", flat=True)), {"pygame", "액션", "puzzle"})
        self.assertEqual(Tag.objects.count(), 3)

    def test_tag_limit_counts_unique_nonempty_tags(self):
        ten_tags = ",".join(f"tag{i}" for i in range(10))
        accepted = self.make_form(tags_str=ten_tags + ",tag0,,")
        self.assertTrue(accepted.is_valid(), accepted.errors)
        rejected = self.make_form(tags_str=ten_tags + ",extra")
        self.assertFalse(rejected.is_valid())
        self.assertIn("10개", str(rejected.errors["tags_str"]))

    def test_edit_replaces_tag_relations_without_deleting_shared_tags(self):
        first_form = self.make_form(tags_str="shared,old")
        self.assertTrue(first_form.is_valid(), first_form.errors)
        project = first_form.save()
        old_tag = Tag.objects.get(name="old")
        form = self.make_form(instance=project, tags_str="shared,new")
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertSetEqual(set(project.tags.values_list("name", flat=True)), {"shared", "new"})
        self.assertTrue(Tag.objects.filter(pk=old_tag.pk).exists())
        self.assertEqual(Tag.objects.filter(name="shared").count(), 1)

    def test_commit_false_defers_project_tags_and_categories_until_explicit_save(self):
        category = Category.objects.create(name="Games")
        form = self.make_form(tags_str="puzzle", categories=[category.pk])
        self.assertTrue(form.is_valid(), form.errors)
        project = form.save(commit=False)
        self.assertIsNone(project.pk)
        self.assertFalse(Project.objects.exists())
        self.assertFalse(Tag.objects.exists())
        project.save()
        form.save_m2m()
        self.assertEqual(list(project.tags.values_list("name", flat=True)), ["puzzle"])
        self.assertEqual(list(project.categories.all()), [category])
