from django.test import TestCase
from htmlvalidator.client import ValidatingClient


class Tests(TestCase):

    def setUp(self):
        super(Tests, self).setUp()
        self.client = ValidatingClient()

    def test_render_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_render_not_valid(self):
        response = self.client.get('/not/')
        self.assertEqual(response.status_code, 200)
