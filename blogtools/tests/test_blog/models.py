from django.db import models
from feincmstools.base import ChunkyContent
from blogtools.models import EntryModel, CategoryModel
from djangosite.assets.files.chunks import ReusableFileChunk, OneOffFileChunk, OEmbedChunk
from djangosite.assets.images.chunks import ReusableImageChunk, OneOffImageChunk
from djangosite.pages.chunks import TextileChunk
from djangosite.smartlinks_conf.fields import SmartLinkMarkupField
from django.utils.translation import ugettext as _

class Category(CategoryModel):
    pass

class Entry(ChunkyContent, EntryModel): #, CommentedItemModel):
    section_title = "Blog"
    category = models.ForeignKey(Category, blank=True, null=True,
        related_name='entries')

    summary = SmartLinkMarkupField(blank=True)

    # FeinCMStools attributes.
    feincms_regions = (
        ('main', _('Main')),
    )

    @classmethod
    def chunks_by_region(cls, region):
        return [
            ('Images', (ReusableImageChunk, OneOffImageChunk)),
            ('Media', (ReusableFileChunk, OneOffFileChunk, OEmbedChunk)),
            (None, (TextileChunk,)),
        ]

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entries"
