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


class TagViewSet(ViewSet):
    permission_classes = [AllowAny,]

    def list(
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


    def create(
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
    

    def retrieve(
        self,
        request: DRFRequest,
        pk: Optional[Union[int, str]] = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Retrieve a tag."""
        
        tag = Tag.objects.get(pk=pk)
        serializer = TagDetailSerializer(tag)

        return DRFResponse(
            serializer.data,
            status=HTTP_200_OK
        )
    
    def destroy(
        self,
        request: DRFRequest,
        pk: Optional[Union[int, str]] = None,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any]
    ) -> DRFResponse:
        """Delete a tag."""
        
        tag = Tag.objects.get(pk=pk)
        tag.delete()
        return DRFResponse(
            {
                "detail": "Tag deleted successfully.",
                
            }, status = HTTP_204_NO_CONTENT
        )
    