=================
Glamkit-blogtools
=================

A tool for quickly creating customised blog apps. It is part of the `GLAMkit project <http://glamkit.org/>`_. For more information, see the `documentation <http://docs.glamkit.org/blogtools/>`_.

See ``tests.test_blog`` for an example application.

Quick start:
============

* Create a new app.

* In models.py create a subclass of EntryModel, and define the fields you need for your blog entry.

* If you want a category, create a subclass of CategoryModel and add a FK from your entry model:

    category = models.ForeignKey(Category, blank=True, null=True,
        related_name='entries')

* In admins.py create a subclass of EntryModelAdmin (or CategoryEntryModelAdmin), and customise. Register your Entry and Category ModelAdmins.

* In APP_NAME/urls.py:

		from blogtools.urls import URLPatterns
		from .models import Entry

		urlpatterns = URLPatterns(
				public_qs=Entry.public_objects.all(),
				private_qs=Entry.objects.all(),
		).patterns

* In your main URLs.py
    url(r'^blog/', include('blog.urls', app_name='blogtools',
        namespace=APP_NAME)),

* Add to INSTALLED_APPS:
    'blogtools',
    'djangosite.blog',
