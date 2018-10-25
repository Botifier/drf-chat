from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models

#TODO: move to utils
def validate_message_content(content):
    if content is None or content == "" or content.isspace():
        raise ValidationError(
            'Content is empty/invalid',
            code='invalid',
            params={'content': content},
        )


class Conversation(models.Model):
    uid = models.CharField(
        max_length=64,
        default=uuid.uuid4,
        unique=True,
        null=True
    )
    participants = models.ManyToManyField(User, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    #TODO: add conversation validator to prevent creation of empty conversations
    class Meta:
        ordering = ('updated_at',)


class Message(models.Model):
    uid = models.CharField(
        max_length=64,
        default=uuid.uuid4,
        unique=True,
        null=True
    )
    conversation = models.ForeignKey(Conversation)
    sender = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField(validators=[validate_message_content])
    class Meta:
        ordering = ('created_at',)




