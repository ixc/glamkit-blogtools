"""
Utility functions to add a generic template to the lookup list
and `current_app` to the context. Mix in before the template view class.

The latter allows for {% url "blogtools:bla" %} to be replaced by
 {% url "myblog:bla" %} in implementing apps.

Your URLs should do this:
    url(r'^press/', include('press_releases.urls', app_name='blogtools',
        namespace='press_releases')),
    url(r'^blog/', include('blog.urls', app_name='blogtools',
        namespace='blog')),

where namespace = implementing app_label.
"""
from django.db.models import Count

from django.views.generic import (ArchiveIndexView, DetailView,
    DayArchiveView, MonthArchiveView, YearArchiveView)
from django.utils.decorators import classonlymethod
from blogtools.models import CategoryModel

class LastResortTemplateMixin(object):
    def get_template_names(self):
        return super(LastResortTemplateMixin, self).get_template_names() +\
               ["blogtools/%s.html" % self.template_name_suffix]

class RenderInjectContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RenderInjectContextMixin, self).get_context_data(**kwargs)
        if not context.has_key('section_title'):
            try:
                context['section_title'] = \
                self.object_list.model.section_title
            except AttributeError:
                context['section_title'] = \
                self.object.section_title

        # inject categories context if applicable
        try:
            if hasattr(self, 'object') and isinstance(self.object, CategoryModel):
                category_qs = type(self.object).objects.get_query_set()
            else:
                category_qs = self.object_list.model.category.get_query_set()
            context['categories'] = category_qs.annotate(
                entry_count=Count('entries')).filter(entry_count__gte=1)
                #TODO: count only active entries
        except AttributeError:
            pass

        return context

    def render_to_response(self, context, **kwargs):
        if not kwargs.has_key('current_app'):
            try:
                kwargs['current_app'] =\
                self.object_list.model._meta.app_label
            except AttributeError:
                kwargs['current_app'] =\
                self.object._meta.app_label
        return super(RenderInjectContextMixin, self).render_to_response(context,
                                                   **kwargs)

class EntryArchive(LastResortTemplateMixin, RenderInjectContextMixin, ArchiveIndexView):
    pass

class EntryYear(LastResortTemplateMixin, RenderInjectContextMixin, YearArchiveView):
    pass

class EntryMonth(LastResortTemplateMixin, RenderInjectContextMixin, MonthArchiveView):
    month_format = '%m'

class EntryDay(LastResortTemplateMixin, RenderInjectContextMixin, DayArchiveView):
    month_format = '%m'

class EntryDetail(RenderInjectContextMixin, DetailView):
    # Defining this is necessary to ensure that the "private_qs" keyword 
    # argument in as_view() does not get rejected as invalid
    private_qs = None

    # To set the used template from the model provide an attribute named 'template_name'
    # pointing to the location of the template
    # e.g. template_name = 'blog/template.html'
    @property
    def template_name(self):
        if hasattr(self.get_object(), 'template_name'):
            return self.get_object().template_name
        return None

    @classonlymethod
    def as_view(cls, **kwargs):
        # We want to call the parent class's as_view() classmethod while 
        # ensuring that it operates on EntryDetail, and not DetailView, so 
        # that the get_queryset() method below gets used. We do this by 
        # grabbing the unbound method using im_func, then binding it to 
        # EntryDetail with __get__.
        return DetailView.as_view.im_func.__get__(cls)(**kwargs)

    def get_queryset(self):
        """
        Logged-in staff can see unpublished entries.
        """
        #TODO: Check for edit permissions.
        if self.request.user.is_staff and self.private_qs is not None:
            return self.private_qs
        else:
            return self.queryset

    def get_context_data(self, **kwargs):
        context = super(EntryDetail, self).get_context_data(**kwargs)
        object = context['object']
        if hasattr(object, 'open_graph'):
            context['open_graph'] = object.open_graph()
        return context

class EntryCategory(RenderInjectContextMixin, DetailView):
    pass