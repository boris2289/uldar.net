# Python imports
from typing import Any


# Django imports
from django.shortcuts import render


# Rest framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny




# Project imports
from apps.comments.models import Comments
from apps.comments.serializers import CommentListSerializer, CommentCreateSerializer, CommentUpdateSerializer


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

    @action(
    methods=("PATCH",),
    permission_classes = (IsAuthenticated,),
    url_path= 'update',
    detail=True
    )
    def update_question(
        self,
        request : DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse:
        """
        Update a comment model
        
        text
        
        this field can be updated
        
        
        """

        try:
            comment = Comments.objects.get(pk = kwargs.get('pk'))
        except Comments.DoesNotExist:
            return DRFResponse(
                {
                    "detail" : "The comment does not exist"
                },
                status = HTTP_404_NOT_FOUND
            )
        
        if comment.author != request.user:
            return DRFResponse({"detail": "You can edit only your comment"}, status=HTTP_403_FORBIDDEN)


        serializer : CommentUpdateSerializer = CommentUpdateSerializer(
            comment,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            {
                "details": "The comment successfully updated",
                "data": serializer.data
            },
            status=HTTP_200_OK
    )
    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    url_path= 'list_by_author',
    detail=False
    )    
    def list_comments_by_author(
        self,
        request: DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse :
        author_id = request.query_params.get('author')

        if not author_id:
            return DRFResponse({"detail": "author is required"}, status=HTTP_400_BAD_REQUEST)
        

        comments = Comments.objects.filter(author = author_id)
        serializer : CommentListSerializer = CommentListSerializer(comments, many = True)

        return DRFResponse(
            serializer.data,
            status = HTTP_200_OK
        )


