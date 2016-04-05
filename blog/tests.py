from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from.models import Post

class PostTests(TestCase):
    def test_str(self):
        test_title=Post(title='MyLatestBlogPost')
        self.assertEquals(
            str(test_title), 'MyLatestBlogPost')
