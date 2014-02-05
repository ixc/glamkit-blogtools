try:
    from django.conf.urls.defaults import url, patterns
except ImportError:
    from django.conf.urls import patterns, url

from .views import (EntryArchive, EntryDetail,
    EntryDay, EntryMonth, EntryYear, EntryCategory)

class URLPatterns(object):
    """
    Make sure to set public_qs = MyEntry.public_objects.all()
    """

    def __init__(self,
         public_qs,
         private_qs=None,
         category_qs=None,
         date_field='byline_date',
         entry_archive=EntryArchive,
         entry_detail=EntryDetail,
         entry_day=EntryDay,
         entry_month=EntryMonth,
         entry_year=EntryYear,
         entry_category=EntryCategory,
         feed=None,
    ):
        # Querysets and Config
        self.public_qs = public_qs
        self.private_qs = private_qs
        self.category_qs = category_qs
        self.date_field = date_field
        self.feed = None

        # URLs
        self.index = url(r'^$',
            entry_archive.as_view(
                queryset=self.public_qs,
                date_field=self.date_field,
                allow_empty=True,
            ),
            name='index'
        )
        self.year = url(r'^(?P<year>\d{4})/$',
            entry_year.as_view(
                queryset=self.public_qs,
                date_field=self.date_field
            ),
            name='year'
        )
        self.month = url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
            entry_month.as_view(
                queryset=self.public_qs,
                date_field=self.date_field
            ),
            name='month'
        )
        self.day = url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
            entry_day.as_view(
                queryset=self.public_qs,
                date_field=self.date_field
            ),
            name='day'
        )
        self.detail = url(r'^(?P<year>\d{4})/(?P<slug>[-\w]+)/$',
            entry_detail.as_view(
                queryset=self.public_qs,
                private_qs=self.private_qs
            ),
            name='detail'
        )

        if self.category_qs is not None and entry_category is not None:
            self.category = url(r'^category/(?P<slug>[-\w]+)/$',
                entry_category.as_view(
                    queryset=self.category_qs,
                    context_object_name='category'
                ),
                name='category'
            )

        if feed:
            self.feed = url(r'^feed/atom.xml$', feed, name='feed')

    @property
    def patterns(self):
        url_patterns = patterns('',
            self.index,
            self.year,
            self.month,
            self.day,
            self.detail,
        )
        if self.category_qs is not None:
            url_patterns += patterns('',
                self.category
            )
        if self.feed is not None:
            url_patterns += patterns('',
                 self.feed
            )
        return url_patterns