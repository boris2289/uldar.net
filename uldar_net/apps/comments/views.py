# Python imports
from typing import Any


# Django imports
from django.shortcuts import render


# Rest framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse


# Project imports
from apps.comments.models import Comments
from apps.comments.serializers import CommentListSerializer, CommentCreateSerializer


class CommentViewSet(ViewSet):
    """ViewSet for Comment model"""
    
    def list(
            self, 
            request : DRFRequest,
            slug : str = None,
            *args : tuple[Any, ...],
            **kwargs : dict[str, Any]
    ) -> DRFResponse:
        
        """Listing all related comments"""

        comments : Comments = Comments.objects
        serializer : CommentListSerializer = CommentListSerializer(comments, many = True)