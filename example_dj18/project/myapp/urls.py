from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^not/$', views.not_valid, name='not_valid'),
]
