from django.db import models
from feincmstools.base import FeinCMSDocument
from blogtools.models import EntryModel, CategoryModel
from djangosite.assets.files.content_types import ReusableFileContent, OneOffFileContent, OEmbedContent
from djangosite.assets.images.content_types import ReusableImageContent, OneOffImageContent
from djangosite.pages.chunks import TextileContent
from djangosite.smartlinks_conf.fields import SmartLinkMarkupField
from django.utils.translation import ugettext as _

class Category(CategoryModel):
    pass

class Entry(FeinCMSDocument, EntryModel): #, CommentedItemModel):
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
            ('Images', (ReusableImageContent, OneOffImageContent)),
            ('Media', (ReusableFileContent, OneOffFileContent, OEmbedContent)),
            (None, (TextileContent,)),
        ]

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entries"
