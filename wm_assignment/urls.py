from django.conf.urls import url, include
from django.contrib.gis import admin
from rest_framework.authtoken import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url('', include('app.urls', namespace="app")),
    url(r'^rest/', include('app.rest_urls', namespace="rest")),
]
