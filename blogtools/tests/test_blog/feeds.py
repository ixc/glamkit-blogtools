from django.core.urlresolvers import reverse_lazy
from blogtools.feeds import AbstractEntriesFeed
from .models import Entry

class LatestEntriesFeed(AbstractEntriesFeed):
    link = reverse_lazy('test_blog:index')
    description_template = "test_blog/__feed_content.html"

    def items(self):
        return Entry.public_objects.order_by('-byline_date')[:5]

    def item_categories(self, item):
        if item.category is not None:
            return [item.category.title]
