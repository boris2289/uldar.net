# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Django imports

# Rest Framework imports
from rest_framework.serializers import ModelSerializer, CharField, IntegerField, TextField

# Project imports
from apps.questions.models import Question
from apps.tags.models import Tag

class QuestionBaseSerializer(ModelSerializer):
    """Base Serializer for Question model."""

    class Meta:
        """Meta class for QuestionBaseSerializer."""
        model = Question
        fields = '__all__'

class QuestionCreateSerializer(QuestionBaseSerializer):
    """Serializer for creating a question."""

    class Meta:
        """Meta class for QuestionCreateSerializer."""
        model = Question
        fields = ['id', 'title', 'description', 'slug', 'tag', 'author']

class QuestionDetailSerializer(QuestionBaseSerializer):
    """Serializer for retrieving a question."""

    class Meta:
        """Meta class for QuestionDetailSerializer."""
        model = Question
        fields = ['id', 'title', 'description', 'slug', 'tag', 'author']

class QuestionListSerializer(QuestionBaseSerializer):
    """Serializer for a list of questions."""

    class Meta:
        """Meta class for QuestionListSerializer."""
        model = Question
        fields = ['id', 'title', 'description', 'slug', 'tag', 'author']
