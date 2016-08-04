from django.conf.urls import url

from htmlvalidator.tests import views


urlpatterns = [
    url(r'^view/', views.html_view, name='html_view')
]
try:
    from django.conf.urls import patterns
    urlpatterns = patterns('', *urlpatterns)
except ImportError:  # Django >= 1.10
    pass
