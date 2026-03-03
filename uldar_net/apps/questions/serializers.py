# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Django imports

# Rest Framework imports
from rest_framework.serializers import ModelSerializer

# Project imports
from apps.questions.models import Question
from apps.tags.models import Tag
from apps.questions.utils import generate_unique_slug

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
        fields = ['id', 'title', 'description', 'tag', 'author']
        extra_kwargs = {
            'description': {'required': False},
            'tag': {'required': False},
        }

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

class QuestionUpdateSerializer(QuestionBaseSerializer):
    """Seriazlier for a question update model"""

    class Meta:
        """Meta class for QuestionUpdateSerializer"""
        model = Question
        fields = ['id', 'title', 'description', 'tag']
        

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            instance.slug = generate_unique_slug(validated_data['title'])

        return super().update(instance, validated_data)
