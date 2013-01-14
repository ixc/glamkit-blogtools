from django.db import models
from blogtools.models import EntryModel, CategoryModel, CommentedItemModel

class Category(CategoryModel):
    pass

class Entry(EntryModel, CommentedItemModel):
    section_title = "Blog"
    category = models.ForeignKey(Category, blank=True, null=True,
        related_name='entries')

    summary = models.TextField(blank=True)
    content = models.TextField()

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entries"
