from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    url(r'^blog/', include('blogtools.tests.test_blog.urls', app_name='blogtools', namespace='test_blog')),
]
