# Python imports
from typing import Any


# Django imports



# Rest framework imports
from rest_framework.serializers import ModelSerializer, EmailField


# Project imports
from apps.comments.models import Comments

class CommentBaseSerializer(ModelSerializer):
    """Base serializer for Comment model"""

    class Meta:
        """Meta class for CommentBaseSerializer"""
        model = Comments
        fields = '__all__'

class CommentListSerializer(CommentBaseSerializer):
    """Serializer for list the Comment models"""
    author_email = EmailField(source = "author.email")

    class Meta:
        """Meta class for CommentListSerializer"""
        model = Comments
        fields = ['id', 'author', 'question', 'text', 'author_email']

class CommentCreateSerializer(CommentBaseSerializer):
    """Serializer for creating a Comment model"""

    class Meta:
        """Meta class for CommentCreateSerializer"""
        model = Comments
        fields = ['id', 'author', 'question', 'text']
        extra_kwargs = {
            'text': {'required': True, 'max_length': Comments.MAX_TEXT_LENGTH},
        }

class CommentUpdateSerializer(CommentBaseSerializer):
    """Serializer for updating comment"""

    class Meta:
        """Meta class for CommentUpdateSerializer"""
        model = Comments
        fields = ['author', 'question', 'text']

