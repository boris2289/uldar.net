# Django imports
from django.forms import (
    ModelForm,
    CharField,
    SlugField
)
from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError


# Project imports 
from apps.tags.models import Tag
from apps.comments.models import Comments
from apps.questions.models import Question

# admin.site.unregister(Question)

class TagCreationForm(ModelForm):
    class Meta:
        model = Tag
        fields = "__all__"


class TagAdmin(ModelAdmin):
    form = TagCreationForm
    list_display = (
        "name",
        "slug",
    )


    
admin.site.register(Tag, TagAdmin)

# admin.site.unregister(Group)