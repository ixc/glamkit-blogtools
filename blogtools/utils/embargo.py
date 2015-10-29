from datetime import datetime
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings


def smart_datetime(*args, **kwargs):
    if settings.USE_TZ:
        # return an aware datetime
        if 'tzinfo' not in kwargs:
            kwargs['tzinfo'] = timezone.get_default_timezone()
        return datetime(*args, **kwargs).astimezone(timezone.get_default_timezone())
    return datetime(*args, **kwargs)


def granular_time(t=None):
    """
    Returns times (or now) rounded to a five minute
    boundary. This helps the backend database to optimize/reuse/cache its
    queries by not creating a brand new query each time.

    Also useful if you are using johnny-cache or a similar queryset cache.
    """
    if t is None:
        t = timezone.now().astimezone(timezone.get_default_timezone())
    return smart_datetime(t.year, t.month, t.day, t.hour, (t.minute // 5) * 5, tzinfo=t.tzinfo)


class EmbargoedContentPublicManager(models.Manager):
    def get_query_set(self):
        return super(EmbargoedContentPublicManager, self).get_query_set().filter(
            Q(is_active=True) & Q(publication_date__lte=granular_time) &
            (Q(publication_end_date__isnull=True) | Q(publication_end_date__gt=granular_time))
        )


class EmbargoedContentPrivateManager(models.Manager):
    def get_query_set(self):
        return super(EmbargoedContentPrivateManager, self).get_query_set().filter(
            Q(is_active=True) & Q(is_private=True)
        )


class EmbargoedContent(models.Model):
    """
    Provides the fields for is_active and publish from/until.

    If you mix in this model, make sure you mix in EmbargoedContentPublicManager
    to the manager that is used for the public site.
    """
    is_active = models.BooleanField(
        _('is active'),
        default=False,
        blank=True,
        help_text=_(
            "Tick to make live on site (see also the publication "
            "date). Note that staff (like yourself) are allowed to "
            "preview inactive content whereas other users and the general "
            "public aren't."
        ),
    )
    is_private = models.BooleanField(
        _('is private'),
        default=False,
        help_text='''
            Private content can be viewed at its direct url, but it will not appear in lists
            until its embargo has passed.
        '''
    )
    publication_date = models.DateTimeField(_('publication date'), default=granular_time)
    publication_end_date = models.DateTimeField(
        _('publication end date'),
        blank=True,
        null=True,
        help_text=_('Leave empty if the entry should stay active forever.')
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.publication_date:
            self.publication_date = granular_time(self.publication_date)
        if self.publication_end_date:
            self.publication_end_date = granular_time(self.publication_end_date)
        super(EmbargoedContent, self).save(*args, **kwargs)

    def is_public(self):
        return self.is_active and \
          self.publication_date <= granular_time() and \
          (not self.publication_end_date or self.publication_end_date > granular_time())
    is_public.boolean = True
