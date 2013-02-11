import datetime

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except:
    from django.contrib.auth.models import User

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

from blogtools.utils.embargo import EmbargoedContent, EmbargoedContentPublicManager
#TODO, put this in glamkit somewhere.


class CategoryModel(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        abstract = True

    def __unicode__(self):
        return self.title

    url_namespace = ''
    @models.permalink
    def get_absolute_url(self):
        # NB that URLs need exactly 2-digit months and dates, so use strftime.
        return ('%s:category' % (self.url_namespace or self._meta.app_label),
            [self.slug,]
        )

    def public_entries(self):
        return self.entries.model.public_objects.filter(category=self)

    @property
    def section_title(self):
        return self.entries.model.section_title


class EntryModel(EmbargoedContent):
    """
    A generic model for blog-esque navigation.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=255, unique=True)
    author = models.ForeignKey(User, related_name='%(app_label)s_entries', blank=True, null=True)
    byline_date = models.DateTimeField(default=timezone.now())

    objects = models.Manager()
    public_objects = EmbargoedContentPublicManager()

    section_title = "Blog"

    class Meta:
        verbose_name = "entry"
        verbose_name_plural = "entries"
        ordering = ['-byline_date',]
        abstract = True

    def __unicode__(self):
        return self.title

    # by default, inheriting models assume the url namespace == the app_label.
    # If you define another namespace, then either copy it to the url_namespace
    # attribute here, or override get_absolute_url
    url_namespace = ''
    @models.permalink
    def get_absolute_url(self):
        # NB that URLs need exactly 2-digit months and dates, so use strftime.
        return ('%s:detail' % (self.url_namespace or self._meta.app_label),
            [self.byline_date.year, self.slug,]
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Append the pk to slugs which have a collision with a pre-existing slug.
        if type(self).objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = '%s-%s' % (self.slug, slugify(self.pk))
        super(EntryModel, self).save(*args, **kwargs)

    def get_content(self):
        return getattr(self, 'content', "")

    def get_summary(self):
        summary = getattr(self, 'summary')
        if not summary:
            return self.get_content()
        return summary


class CommentedItemModel(models.Model):
    allow_comments = models.BooleanField(default=True)

    class Meta:
        abstract = True
