from django.conf.urls import include, url


urlpatterns = [
    url(r'', include('project.myapp.urls')),
]
