import os
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.utils.importlib import import_module
from testtools import apploader

"""
These tests cause a few naive datetime warnings, because generic views don't use
timezone-aware dates. This is fixed in
https://code.djangoproject.com/ticket/18217 - Django 1.5.
"""

APP_NAMES = ('blogtools', 'blogtools.tests.test_blog', )
app_template_dirs = []

for APP_NAME in APP_NAMES:
    app_template_dir = None
    try:
        mod = import_module(APP_NAME)
    except ImportError, e:
        raise ImproperlyConfigured('ImportError %s: %s' % (APP_NAME, e.args[0]))
    template_dir = os.path.join(os.path.dirname(mod.__file__), 'templates')
    if os.path.isdir(template_dir):
        app_template_dirs.append(template_dir)


@override_settings(
    TEMPLATE_DIRS = app_template_dirs #Ignore the default _base.html
)
class SimpleTest(TestCase):
    fixtures = ['blog_test_content.json']
    urls = 'blogtools.tests.urls'

    def _pre_setup(self):
        # The following line would naturally be in setUp(), except we have to
        # install the app before its fixtures will load.
        apploader.load_app(APP_NAME)
        super(SimpleTest, self)._pre_setup() #This loads the fixtures

    def _post_teardown(self):
        super(SimpleTest, self)._post_teardown()
        apploader.unload_app(APP_NAME)

    def test_index(self):
        client = Client()
        response = client.get(reverse("test_blog:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 3) # only public objects
        self.assertNotContains(response, "You should not see me.") # only public objects

        self.assertContains(response, "But I do have content" ) #The body content should become the summary if there is no summary.


    def test_feed(self):
        client = Client()
        response = client.get(reverse("test_blog:feed"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "You should not see me.") # only public objects
        self.assertContains(response, "But I do have content") # full content, not just summary

    def test_archive_year(self):
        client = Client()
        response = client.get(reverse("test_blog:year", args=("2012", )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "December")

    def test_archive_month(self):
        client = Client()
        response = client.get(reverse("test_blog:month", args=("2012", "12", )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 2) # only public objects
        self.assertNotContains(response, "You should not see me.") # only public objects

        response = client.get(reverse("test_blog:month", args=("2012", "11", )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 1) # only public objects

        response = client.get(reverse("test_blog:month", args=("2012", "10", )))
        self.assertEqual(response.status_code, 404)


    def test_archive_day(self):
        client = Client()
        response = client.get(reverse("test_blog:day", args=("2012", "11", "19" )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "I have no summary")

        response = client.get(reverse("test_blog:day", args=("2012", "11", "18" )))
        self.assertEqual(response.status_code, 404)

    def test_category(self):
        client = Client()
        response = client.get(reverse("test_blog:category", args=("cat-1", )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'].slug, 'cat-1') # only public objects

        response = client.get(reverse("test_blog:category", args=("cat-2", )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no posts in <em>Category 2</em>.")

        response = client.get(reverse("test_blog:category", args=("not-a-category", )))
        self.assertEqual(response.status_code, 404)


    def test_post(self):
        client = Client()

        public_entry = models.get_model("test_blog", "Entry").objects.get(slug="i-have-no-summary")
        response = client.get(public_entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "I have no summary")

        private_entry = models.get_model("test_blog", "Entry").objects.get(slug="i-am-not-active")
        response = client.get(private_entry.get_absolute_url())
        self.assertEqual(response.status_code, 404)


#   Not done yet
#    def test_author(self):
#        pass