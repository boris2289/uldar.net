# Python imports
from typing import Any, Dict, List, Optional, Tuple, Union


# Django imports
from django.shortcuts import render
from django.utils.text import slugify


# Rest Framework imports
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response as DRFResponse
from rest_framework.request import Request as DRFRequest
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND


# Project imports
from apps.tags.models import Tag
from apps.tags.serializers import TagCreateSerializer, TagDetailSerializer, TagListSerializer
from apps.questions.models import Question
from apps.questions.serializers import QuestionListSerializer

class TagViewSet(ViewSet):
    lookup_field = 'slug'
    permission_classes = [AllowAny,]

    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    detail=False,
    url_path='list'
    )
    def list_tags(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """List all tags."""
        
        tags = Tag.objects.all()
        serializer = TagListSerializer(tags, many=True)

        return DRFResponse(
            serializer.data,
            status=HTTP_200_OK
        )    

    @action(
    methods=("POST",),
    permission_classes = (IsAuthenticated,),
    detail=False,
    url_path='create'
    )
    def create_tag(
        self,
        request: DRFRequest,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Create a new tag."""
        


        serializer = TagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        
        existing_tag = Tag.objects.filter(name = data['name']).first()
        
        if existing_tag:
            return DRFResponse(
            TagDetailSerializer(existing_tag).data,
            status=HTTP_201_CREATED
        ) 
        else:

            tag = Tag.objects.create(
                name = data['name'],
                slug = slugify(data['name'])
            )

            return DRFResponse(
                TagDetailSerializer(tag).data,
                status=HTTP_201_CREATED
            )
    
    @action(
    methods=("GET",),
    permission_classes = (AllowAny,),
    detail=True,
    url_path='retrieve'
    )
    def retrieve_tag(
        self,
        request: DRFRequest,
        slug : str = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Retrieve a tag."""



        try:
            tag = Tag.objects.get(slug = slug)
        except Tag.DoesNotExist:
            return DRFResponse(
                {"detail" : "Tag does not exist"},
                status=HTTP_400_BAD_REQUEST
            )
        
        serializer = TagDetailSerializer(tag)

        questions = Question.objects.filter(tag = tag)
        questions_serializer = QuestionListSerializer(questions, many = True)




        return DRFResponse(
            {
            "tag" : serializer.data,
            "questions" : questions_serializer.data
            },
            status=HTTP_200_OK
        )
    

    