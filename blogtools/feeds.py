from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.conf import settings

class AbstractEntriesFeed(Feed):
    feed_type = Atom1Feed
    title = settings.SITE_NAME
    description = "Updates to the %s blog." % settings.SITE_NAME

    subtitle = description

#    def items(self):
#        return Entry.public_objects.order_by('-byline_date')[:5]

    def item_title(self, item):
        return item.title

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author

#    def item_author_link(self, item):
#        return settings.SITE_URL + item.author.get_absolute_url()

#    def item_categories(self, item):
#        if item.category is not None:
#            return [item.category.title]

    def item_pubdate(self, item):
        return item.byline_date