
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-token-auth/', obtain_jwt_token, name='api-token-auth'),
    url(r'^api-token-verify/', verify_jwt_token, name='api-token-verify'),
]
