# Python imports
from typing import Any


# Django imports
from django.shortcuts import render


# Rest framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated




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

        comments : Comments = Comments.objects.all()
        serializer : CommentListSerializer = CommentListSerializer(comments, many = True)

        return DRFResponse(
            serializer.data,
            {"detail" : "Comments succesfully returned"},
            status=HTTP_200_OK
        )
    
    @action(
        url_path="create",
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=("POST",)
    )
    def create_comment(
        self,
        request: DRFRequest,
        slug: None,
        *args : tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Create a comment method"""
        
        serializer : CommentCreateSerializer = CommentCreateSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        comment : Comments = Comments.objects.create(
            text = data['text'],
            author = data['author'],
            question = data['question']
        )

        return DRFResponse(
            serializer.data,
            {"detail" : "Comment sucsesfully created"},
            status= HTTP_200_OK
        )



