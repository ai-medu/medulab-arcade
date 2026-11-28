import json
import tempfile

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

URL = '/meducode/api/examples/'
NAME = '올로AI 1단계 코딩'


def project(text='a'):
    return json.dumps({'name': NAME, 'objects': [], 'scripts': {'1:2': text}}, ensure_ascii=False)


class MeduCodeExampleTests(TestCase):
    def setUp(self):
        folder = override_settings(MEDUCODE_EXAMPLES=tempfile.mkdtemp())
        folder.enable()
        self.addCleanup(folder.disable)
        self.admin = User.objects.create_user('boss', password='pw-for-test', is_staff=True)
        self.client.force_login(self.admin)

    def save(self, data, example_id=NAME, client=None):
        return (client or self.client).post(URL, json.dumps({'id': example_id, 'data': data}), content_type='application/json')

    def load(self, client=None, example_id=NAME):
        return (client or self.client).get(URL, {'id': example_id}).json()['data']

    def test_admin_updates_and_everyone_reads(self):
        self.assertIsNone(self.load())
        self.assertEqual(self.save(project('a')).status_code, 200)
        self.assertEqual(self.save(project('b')).status_code, 200)
        self.assertEqual(self.load(Client()), project('b'))

    def test_only_admin_can_save(self):
        student = Client()
        student.force_login(User.objects.create_user('kid', password='pw-for-test'))
        for client, status in ((Client(), 401), (student, 403)):
            self.assertEqual(self.save(project(), client=client).status_code, status)
        self.assertIsNone(self.load())

    def test_bad_values(self):
        for data, example_id in (('x', NAME), ('[]', NAME), ('{}', NAME), (5, NAME), (project(), ''), (project(), 'a\nb')):
            self.assertEqual(self.save(data, example_id).status_code, 400, (data, example_id))
        self.assertEqual(self.client.post(URL, '[]', content_type='application/json').status_code, 400)
        self.assertEqual(self.save(project('a' * (2 * 1024 * 1024))).status_code, 413)

    def test_path_like_name_stays_inside_folder(self):
        self.assertEqual(self.save(project(), '../../escape').status_code, 200)
        self.assertEqual(self.load(example_id='../../escape'), project())

    def test_csrf_is_checked(self):
        strict = Client(enforce_csrf_checks=True)
        strict.force_login(self.admin)
        self.assertEqual(self.save(project(), client=strict).status_code, 403)
