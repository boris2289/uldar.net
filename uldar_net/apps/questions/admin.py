# Django imports
from django.forms import ModelForm, CharField, SlugField
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


class QuestionCreationForm(ModelForm):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionAdmin(ModelAdmin):
    form = QuestionCreationForm
    filter_vertical = ("tag",)
    list_display = (
        "title",
        "description",
        "slug",
        "display_tags",
        "is_active",
        "author",
    )

    def display_tags(self, obj):
        """Creates a string for the tags to be displayed in the list."""
        return ", ".join([tags.name for tags in obj.tag.all()])

    display_tags.short_description = "Tag"


admin.site.register(Question, QuestionAdmin)
