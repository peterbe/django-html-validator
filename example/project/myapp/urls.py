from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.home_page, name='home_page'),
    url(r'^not/$', views.not_valid, name='not_valid'),
)
