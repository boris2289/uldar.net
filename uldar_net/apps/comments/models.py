# Python imports
from typing import Any

# Django imports
from django.db.models import (
    Model,
    CharField, 
    TextField,
    DateTimeField, 
    ManyToManyField,
    ForeignKey, 
    CASCADE,
    PROTECT
    )

# Project imports
from apps.questions.models import Question
from apps.users.models import CustomUser

class Comments(Model):
    MAX_TEXT_LENGTH = 300
    
    question = ForeignKey(
        to=Question,
        on_delete=CASCADE
    )

    author = ForeignKey(
        to=CustomUser,
        on_delete=PROTECT
    )

    text = TextField(
        max_length=MAX_TEXT_LENGTH
    )

    created_at = DateTimeField(
        auto_now=True
    )

    updated_at = DateTimeField(
        auto_now_add=True
    )

