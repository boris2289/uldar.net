# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

# Django imports
from django.utils.text import slugify
from django.core.exceptions import ValidationError

# Rest Framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

# Project imports
from apps.questions.models import Question
from apps.questions.serializers import QuestionCreateSerializer, QuestionDetailSerializer, QuestionListSerializer, QuestionUpdateSerializer
from apps.tags.models import Tag
from apps.tags.serializers import TagDetailSerializer
from apps.comments.serializers import CommentListSerializer
from apps.comments.models import Comments
from apps.comments.serializers import CommentListSerializer, CommentCreateSerializer




class QuestionViewSet(ViewSet):
    lookup_field = 'slug'

    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    url_path= 'list',
    detail=False
    )    
    def list_questions(
        self,
        request: DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse :
        
        questions = Question.objects.all()
        serializer : QuestionListSerializer = QuestionListSerializer(questions, many = True)

        return DRFResponse(
            serializer.data,
            status = HTTP_200_OK
        )
    

    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    url_path= 'retrieve',
    detail=True
    )
    def retrieve_question(
        self,
        request: DRFRequest,
        slug : str = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse :
        try:
            question = Question.objects.get(slug = slug)
        except Question.DoesNotExist:
            return DRFResponse(
                {"detail" : "Question does not found"},
                status = HTTP_404_NOT_FOUND
            )

        serializer : QuestionDetailSerializer = QuestionDetailSerializer(question)
        
        comments : List[Comments] = Comments.objects.filter(question = question) 

        comment_serializer : CommentListSerializer = CommentListSerializer(comments, many = True)
        

        return DRFResponse(
            {
                "question" : serializer.data,
                "comments" : comment_serializer.data,
            },
            status=HTTP_200_OK
        )
    
    @action(
    methods=("DELETE",),
    permission_classes = (IsAuthenticated,),
    url_path= 'destroy',
    detail=True
    )    
    def destroy_question(
        self,
        request : DRFRequest,
        slug : str = None,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse :
        
        """Deleting the Question by slug"""

        try:
            question = Question.objects.get(slug = slug)
        except Question.DoesNotExist:
            return DRFResponse(
                {"detail" : "Question does not exist"},
                status=HTTP_404_NOT_FOUND
            )
        
        if question.author != DRFRequest.user:
            return DRFResponse(
                {"detail" : "You're not an author of this question"}
            ) 

        question.delete()

        return DRFResponse(
            status=HTTP_204_NO_CONTENT
        )
    
    @action(
    methods=("POST",),
    permission_classes = (IsAuthenticated,),
    url_path='create',
    detail=False
    )    
    def create_question(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Create a new question."""
        


        serializer: QuestionCreateSerializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        def generate_unique_slug(title):
            base_slug = slugify(title)
            slug = base_slug
            while Question.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            return slug
        
        question : Question = Question.objects.create(
            title = data['title'],
            description = data.get('description'),
            slug = generate_unique_slug(data['title']),
            author = data['author'],
        )

        question.tag.set(data.get('tag'))

        return DRFResponse(
            QuestionDetailSerializer(question).data,
            status = HTTP_201_CREATED
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
        slug : str = None,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse:
        """
        Update a question model
        
        title
        description
        tag
        is_active

        this fields can be updated
        
        
        """

        try:
            question = Question.objects.get(slug = slug)
        except Question.DoesNotExist:
            return DRFResponse(
                {
                    "detail" : "The question does not exist"
                },
                status = HTTP_400_BAD_REQUEST
            )
        
        if question.author != request.user:
            return DRFResponse({"detail": "You can edit only your question"}, status=HTTP_403_FORBIDDEN)


        serializer : QuestionUpdateSerializer = QuestionUpdateSerializer(
            question,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            {
                "details": "The question successfully updated",
                "data": serializer.data
            },
            status=HTTP_200_OK
    )
    @action(
        url_path="create_comment",
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
            status= HTTP_200_OK
        )
    
    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    url_path= 'list_by_author',
    detail=False
    )    
    def list_questions_by_author(
        self,
        request: DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse :
        
        author_id = request.query_params.get('author')
        
        questions = Question.objects.filter(author = author_id)
        serializer : QuestionListSerializer = QuestionListSerializer(questions, many = True)

        return DRFResponse(
            serializer.data,
            status = HTTP_200_OK
        )
    





