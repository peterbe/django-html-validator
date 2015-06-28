from django.conf.urls import patterns, url

from htmlvalidator.tests import views


urlpatterns = patterns(
    '',
    url(r'^view/', views.html_view, name='html_view')
)
