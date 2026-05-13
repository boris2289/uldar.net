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
from apps.comments.models import Comments
from apps.questions.models import Question


class CommentCreationForm(ModelForm):
    class Meta:
        model = Comments
        fields = "__all__"
    


class CommentAdmin(ModelAdmin):
    form = CommentCreationForm
    list_display = (
        "question", 
        "author",
        "short_text",
    )

    def short_text(self, obj):
        """Truncates comment text for the list view."""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    
    short_text.short_description = 'Comment Content'

    
admin.site.register(Comments, CommentAdmin)

# admin.site.unregister(Group)