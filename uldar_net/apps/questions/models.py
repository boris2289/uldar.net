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
    BooleanField,
    Manager,
    Count
)
from django.utils.translation import gettext_lazy as _

# Project imports
from apps.tags.models import Tag
from apps.users.models import CustomUser
from apps.abstract.models import AbstractBaseModel

class QuestionManager(Manager):
    def get_queryset(self):
        # Optimization: select_related for FK, prefetch_related for M2M
        """
        select_related works by creating a SQL JOIN in your initial query. It follows "one-to-one" or "many-to-one" relationships to pull in the related object's data immediately.
        How it works: It fetches everything in one single SQL query.
        When to use: Use it for ForeignKey and OneToOneField.
        """

        # Annotation: adding a 'tag_count' field dynamically
        """
        How Count works with prefetch_related:
            annotate happens at the Database level (SQL).
            prefetch_related happens at the Python level (after the first query).
        
        Because we have tag_count in the annotation, the database calculates the number of tags. 
        Because we have prefetch_related('tag'), Django also downloads the full tag objects. 
        This is perfectly fine and exactly what we need if our API endpoint needs to show both the total number of tags and the list of tag names.
        """
        return super().get_queryset().select_related('author').prefetch_related('tag').annotate(
            tag_count=Count('tag')
        )


class Question(AbstractBaseModel):
    """Model representing a question."""
    MAX_TITLE_LENGTH = 255

    title = CharField(
        max_length=MAX_TITLE_LENGTH,
        help_text=_("The title of the question.")
    )

    description = TextField(
        blank=True,
        null=True,
        help_text=_("The description of the question.")
    )

    slug = SlugField(
        verbose_name=_("Slug"),
        unique=True,
        help_text=_("The slug of the question.")
    )

    tag = ManyToManyField(
        Tag,
        related_name="questions",
        help_text=_("The tags of the question."),
        blank=True,
    )

    is_active = BooleanField(
        default=True,
        help_text=_("Whether the question is active or not.")
    )
    
    author = ForeignKey(
        to=CustomUser,
        on_delete=CASCADE,
        related_name="questions"
    )

    objects = QuestionManager()

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        """Meta class for Question model."""
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        