from django.conf.urls import url

from htmlvalidator.tests import views


urlpatterns = [
    url(r'^view/', views.html_view, name='html_view')
]
