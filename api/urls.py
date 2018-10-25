from django.conf.urls import url, include
from django.conf import settings
from .views import ConversationList, MessageList, MessageDetail


urlpatterns = [
    url('conversations/', ConversationList.as_view(), name="conversation-list"),
    url('messages/', MessageList.as_view(), name="message-list"),
    url('message/', MessageDetail.as_view(), name="message-detail"),    
]
