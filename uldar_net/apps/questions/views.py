# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union

# Django imports

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


class QuestionViewSet(ViewSet):
    @action(
        methods=('GET', ),
        permission_classes = (AllowAny, ),
        
    )
    
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
            ,{"detail" : "All questions succesfully listed"},
            status=HTTP_200_OK
        )
    

    @action(
            
        methods = ('GET', ),
        permission_classes = (AllowAny, ),
        detail = True,
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
    
    
    @action(
        methods=('DELETE', ),
        permission_classes = (IsAuthenticated, ),
        detail=True
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



