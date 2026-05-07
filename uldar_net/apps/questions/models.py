# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Django imports
from django.db.models import (
    CharField,
    IntegerField,
    ForeignKey,
    CASCADE,
    SlugField,
    TextField,
    ManyToManyField,
    DateTimeField,
    BooleanField
)

# Project imports
from apps.tags.models import Tag
from apps.users.models import CustomUser
from apps.abstract.models import AbstractBaseModel

class Question(AbstractBaseModel):
    """Model representing a question."""
    MAX_TITLE_LENGTH = 255

    title = CharField(
        max_length=MAX_TITLE_LENGTH,
        help_text="The title of the question."
    )

    description = TextField(
        blank=True,
        null=True,
        help_text="The description of the question."
    )

    slug = SlugField(
        verbose_name="Slug",
        unique=True,
        help_text="The slug of the question."
    )

    tag = ManyToManyField(
        Tag,
        related_name="questions",
        help_text="The tags of the question.",
        blank=True,
    )

    is_active = BooleanField(
        default=True,
        help_text="Whether the question is active or not."
    )
    
    author = ForeignKey(
        to=CustomUser,
        on_delete=CASCADE,
        related_name="questions"
    )

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        """Meta class for Question model."""
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        # To-Do Ordering by Abstract model fields