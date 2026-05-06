# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Django imports
from django.db import models
from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE, SlugField, TextField

class Tag(Model):
    MAX_NAME_LENGTH = 255

    name = CharField(
        max_length=MAX_NAME_LENGTH,
        help_text="The name of the tag."
        )
    
    slug = SlugField(
        help_text="The slug of the tag.",
        unique=True
    )
    

    def __str__(self) -> str:
        return self.name
    



