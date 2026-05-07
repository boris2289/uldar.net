from django.utils.text import slugify
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet

from apps.questions.models import Question
from apps.questions.serializers import QuestionListSerializer
from apps.tags.models import Tag
from apps.tags.serializers import TagCreateSerializer, TagDetailSerializer, TagListSerializer
from apps.tags.schema import tag_schema

tag_retrieve_response = inline_serializer(
    name="TagRetrieveResponse",
    fields={
        "tag": TagDetailSerializer(),
        "questions": QuestionListSerializer(many=True),
    },
)

error_response = inline_serializer(
    name="TagErrorResponse",
    fields={"detail": serializers.CharField()},
)

validation_error_response = inline_serializer(
    name="TagValidationErrorResponse",
    fields={
        "name": serializers.ListField(
            child=serializers.CharField(),
            required=False,
        ),
        "detail": serializers.CharField(required=False),
    },
)

@tag_schema
class TagViewSet(ViewSet):
    queryset = Tag.objects.all()
    lookup_field = "slug"

    @action(methods=["GET"], permission_classes=[IsAuthenticatedOrReadOnly], detail=False, url_path="list")
    def list_tags(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        tags = Tag.objects.all()
        serializer = TagListSerializer(tags, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="create")
    def create_tag(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        serializer = TagCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tag = Tag.objects.filter(name=data["name"]).first()
        if tag is None:
            tag = Tag.objects.create(name=data["name"], slug=slugify(data["name"]))

        return DRFResponse(TagDetailSerializer(tag).data, status=HTTP_201_CREATED)

    @action(methods=["GET"], permission_classes=[AllowAny], detail=True, url_path="retrieve")
    def retrieve_tag(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        try:
            tag = Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            return DRFResponse({"detail": "Tag does not exist"}, status=HTTP_404_NOT_FOUND)

        questions = Question.objects.filter(tag=tag)
        return DRFResponse(
            {
                "tag": TagDetailSerializer(tag).data,
                "questions": QuestionListSerializer(questions, many=True).data,
            },
            status=HTTP_200_OK,
        )