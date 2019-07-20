from django.conf.urls import url, include
from django.conf import settings
from .views import index


urlpatterns = [
    url('^$', index, name='index')    
]