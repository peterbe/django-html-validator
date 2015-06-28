from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):

    def shortDescription(self):
        # Stop nose using the test docstring and instead the test method
        # name.
        pass
