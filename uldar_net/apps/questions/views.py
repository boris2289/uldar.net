# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

# Django imports
from django.utils.text import slugify

# Rest Framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

# Project imports
from apps.questions.models import Question
from apps.questions.serializers import QuestionCreateSerializer, QuestionDetailSerializer, QuestionListSerializer
from apps.tags.models import Tag
from apps.tags.serializers import TagDetailSerializer


class QuestionViewSet(ViewSet):

    
    def list(
        self,
        request: DRFRequest,
        *args : tuple[Any, ...],
        **kwargs : dict[str, Any]
    ) -> DRFResponse :
        
        questions = Question.objects.all()
        serializer : QuestionListSerializer = QuestionListSerializer(questions, many = True)

        return DRFResponse(
            serializer.data
            ,
            {"detail" : "All questions succesfully listed"},
            status=HTTP_200_OK
        )
    


    def retrieve(
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

        return DRFResponse(
            serializer.data,
            status=HTTP_200_OK
        )
    
    
    def destroy(
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
        
        if question.author != request.user:
            return DRFResponse(
                {"detail" : "You're not an author of this question"}
            ) 

        question.delete()

        return DRFResponse(
            status=HTTP_204_NO_CONTENT
        )
    
    
    def create(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Create a new question."""
        


        serializer = QuestionCreateSerializer(data=request.data)
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
            description = data['description'],
            slug = generate_unique_slug(data['title']),
            author = data['author'],
        )

        question.tag.set(data['tag'])

        return DRFResponse(
            QuestionDetailSerializer(question).data,
            status = HTTP_201_CREATED
        )



