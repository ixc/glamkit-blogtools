import datetime

from django.shortcuts import get_object_or_404
from django.views.generic import date_based, list_detail
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.syndication.views import feed as django_feed

from utils import get_query



def prepare_queryset(view):
    ''' Decorator for preparing the queryset before it is used by the views '''
    def wrapper(self, *args, **kwargs):
        if 'entry_queryset' in kwargs:
            queryset = kwargs['entry_queryset']
        else:
            queryset = self.entry_queryset
        if callable(queryset):
            # Allow passing callable instead of a queryset. Useful when using special managers.
            queryset = queryset()
        kwargs['entry_queryset'] = queryset
        return view(self, *args, **kwargs)
    return wrapper
    



class BaseEntryViews(object):
    entry_queryset = None
    template_root_path = None
    publication_date_field = 'pub_date'
    slug_field = 'slug'
    paginate_by = None
    month_format = '%m'
    
    @prepare_queryset
    def archive_index(self, request, *args, **kwargs):
        info_dict = {
                'queryset': kwargs.pop('entry_queryset'),
                'template_name': '%s/entry_archive_index.html' % self.template_root_path,
                'template_object_name': 'entry',
                'paginate_by': self.paginate_by,
             }
        return list_detail.object_list(request, *args, **dict(info_dict, **kwargs))

    @prepare_queryset
    def archive_year(self, request, *args, **kwargs):
        #TODO: Enable pagination when Django's ticket #2367 is fixed.
        info_dict = {
                'queryset': kwargs.pop('entry_queryset'),
                'date_field': self.publication_date_field,
                'template_name': '%s/entry_archive_year.html' % self.template_root_path,
                'template_object_name': 'entry',
            }
        return date_based.archive_year(request, *args, **dict(info_dict, make_object_list=True, **kwargs))

    @prepare_queryset
    def archive_month(self, request, *args, **kwargs):
        #TODO: Enable pagination when Django's ticket #2367 is fixed.
        info_dict = {
                'queryset': kwargs.pop('entry_queryset'),
                'date_field': self.publication_date_field,
                'template_name': '%s/entry_archive_month.html' % self.template_root_path,
                'template_object_name': 'entry',
            }
        return date_based.archive_month(request, *args, **dict(info_dict, month_format=self.month_format, **kwargs))

    @prepare_queryset
    def archive_day(self, request, *args, **kwargs):
        #TODO: Enable pagination when Django's ticket #2367 is fixed.
        info_dict = {
                'queryset': kwargs.pop('entry_queryset'),
                'date_field': self.publication_date_field,
                'template_name': '%s/entry_archive_day.html' % self.template_root_path,
                'template_object_name': 'entry',
            }
        return date_based.archive_day(request, *args, **dict(info_dict, month_format=self.month_format, **kwargs))

    @prepare_queryset
    def entry_detail(self, request, *args, **kwargs):
        info_dict = {
                'queryset': kwargs.pop('entry_queryset'),
                'date_field': self.publication_date_field,
                'template_name': '%s/entry_detail.html' % self.template_root_path,
                'template_object_name': 'entry',
            }
        return date_based.object_detail(request, *args, **dict(info_dict, month_format=self.month_format, slug_field=self.slug_field, **kwargs))

    @prepare_queryset
    def search(self, request, *args, **kwargs):
        #TODO: enable pagination
        query_string = ''
        found_entries = None
        if ('q' in request.GET) and request.GET['q'].strip():
            query_string = request.GET['q']

            entry_query = get_query(query_string, ['title', 'body',])

            found_entries = kwargs['entry_queryset'].filter(entry_query)

        context = {
            'query_string': query_string,
            'found_entries': found_entries
        }
        if 'extra_context' in kwargs:
            context.update(kwargs['extra_context'] or {})

        return render_to_response('%s/search_results.html' % self.template_root_path,
                              context,
                              context_instance=RequestContext(request))
    
    @prepare_queryset
    def entry_preview(self, request, entry_pk, *args, **kwargs):
        @staff_member_required
        def func(request, entry_pk, *args, **kwargs):
            context = {
                'preview': True
            }
            if 'extra_context' in kwargs:
                context.update(kwargs['extra_context'] or {})
            return list_detail.object_detail(
                     request,
                     object_id=entry_pk,
                     queryset=kwargs.pop('entry_queryset'),
                     template_object_name='entry',
                     template_name='%s/entry_detail.html' % self.template_root_path,
                     extra_context=context
                 )
        return func(request, entry_pk, *args, **kwargs)

try:
    from tagging.models import Tag
    from tagging.views import tagged_object_list

    class TaggedEntryViewsMixin(object):

        def tag_list(self, request, *args, **kwargs):
            extra_context = {}
            if 'extra_context' in kwargs:
                extra_context.update(kwargs['extra_context'] or {})
            return list_detail.object_list(
               { 'queryset': Tag.objects.all().order_by('name'),
                 'template_name': '%s/tag_list.html' % self.template_root_path,
                 'template_object_name': 'tag',
                 'extra_context': extra_context,
                 'paginate_by': self.paginate_by, }
            )

        def tagged_entry_list(self, request, *args, **kwargs):
            if 'entry_queryset' in kwargs:
                queryset = kwargs['entry_queryset']
                del kwargs['entry_queryset']
            else:
                queryset = self.entry_queryset
            info_dict = {
                'queryset_or_model': queryset,
                'template_name': '%s/tag_detail.html' % self.template_root_path,
                'template_object_name': 'entry',
                'paginate_by': self.paginate_by,
                 }
            return tagged_object_list(request, *args, **dict(info_dict, **kwargs))

        def json_tag_list(self, request):
            tags = [tag.name for tag in Tag.objects.all()]
            json = simplejson.dumps({ 'success': True, 'tags': tags })
            return HttpResponse(json, mimetype='text/plain')
except ImportError:
    pass
