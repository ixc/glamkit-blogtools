from django.conf.urls import patterns, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
     (r'^blog/', include('blogtools.tests.test_blog.urls', app_name='blogtools', namespace='test_blog')),
)