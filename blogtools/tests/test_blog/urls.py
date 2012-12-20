from blogtools.urls import URLPatterns
from .models import Entry, Category
from .feeds import LatestEntriesFeed

urlpatterns = URLPatterns(
    public_qs=Entry.public_objects.all(),
    private_qs=Entry.objects.all(),
    category_qs=Category.objects.all(),
    feed=LatestEntriesFeed(),
).patterns
