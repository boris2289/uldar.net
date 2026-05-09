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
from logging import getLogger

from apps.questions.models import Question
from apps.questions.serializers import QuestionListSerializer
from apps.tags.models import Tag
from apps.tags.serializers import TagCreateSerializer, TagDetailSerializer, TagListSerializer
from apps.tags.schema import tag_schema
from apps.common.responses import ERROR_401, ERROR_403, ERROR_404, ERROR_429, VALIDATION_400


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

logger = getLogger("django")

class TagViewSet(ViewSet):
    queryset = Tag.objects.all()
    lookup_field = "slug"
    
    def _get_log_context(self, request: DRFRequest) -> dict:
        """Helper to create consistent base logging context."""
        context = {
            "path": request.path,
            "method": request.method,
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT'),
        }
        if request.user.is_authenticated:
            context["user_id"] = request.user.id
        return context
    
    @extend_schema(
        tags=["Tags"],
        summary="List all tags",
        description="Returns a list of all tags. Authentication is not required.",
        responses={
            200: OpenApiResponse(response=TagListSerializer(many=True), description="Tags were returned successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "List tags response example",
                response_only=True,
                status_codes=["200"],
                value=[
                    {"id": 1, "name": "Python", "slug": "python"},
                    {"id": 2, "name": "Django", "slug": "django"},
                ],
            ),
        ],
    )
    @action(methods=["GET"], permission_classes=[IsAuthenticatedOrReadOnly], detail=False, url_path="list")
    def list_tags(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        log_extra = self._get_log_context(request)
        tags = Tag.objects.all()
        serializer = TagListSerializer(tags, many=True)
        logger.info(f"Tags list retrieved. Count: {tags.count()}", extra=log_extra)
        return DRFResponse(serializer.data, status=HTTP_200_OK)


    @extend_schema(
        tags=["Tags"],
        summary="Create a new tag",
        description="Creates a new tag. If a tag with the same name exists, the existing tag is returned.",
        request=TagCreateSerializer,
        responses={
            201: OpenApiResponse(response=TagDetailSerializer, description="Tag was created successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample("Create tag request example", request_only=True, value={"name": "Machine Learning"}),
            OpenApiExample("Create tag response example", response_only=True, status_codes=["201"], value={"id": 3, "name": "Machine Learning", "slug": "machine-learning"}),
        ],
    )
    @action(methods=["POST"], permission_classes=[IsAuthenticated], detail=False, url_path="create")
    def create_tag(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        log_extra = self._get_log_context(request)
        serializer = TagCreateSerializer(data=request.data)
        if not serializer.is_valid():
            log_extra["errors"] = serializer.errors
            logger.warning("Tag creation failed: Validation error", extra=log_extra)
            serializer.is_valid(raise_exception=True)

        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        tag = Tag.objects.filter(name=data["name"]).first()
        if tag is None:
            logger.info(f"New tag created", extra=log_extra)
            tag = Tag.objects.create(name=data["name"], slug=slugify(data["name"]))
        else:
            logger.info(f"Existing tag returned for name", extra=log_extra)
        return DRFResponse(TagDetailSerializer(tag).data, status=HTTP_201_CREATED)


    @extend_schema(
        tags=["Tags"],
        summary="Retrieve tag by slug",
        description="Returns detailed information about a tag and the list of questions linked to it.",
        responses={
            200: OpenApiResponse(response=tag_retrieve_response, description="Tag and related questions were returned successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "Retrieve tag response example",
                response_only=True,
                status_codes=["200"],
                value={
                    "tag": {"id": 1, "name": "Django", "slug": "django"},
                    "questions": [{"id": 10, "title": "How to use serializers?", "slug": "how-to-use-serializers"}],
                },
            ),
            OpenApiExample("Retrieve tag not found example", response_only=True, status_codes=["404"], value={"detail": "Tag does not exist"}),
        ],
    )
    @action(methods=["GET"], permission_classes=[AllowAny], detail=True, url_path="retrieve")
    def retrieve_tag(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        log_extra = self._get_log_context(request)
        try:
            logger.info(f"Tag retrieved: {slug}", extra=log_extra)
            tag = Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            logger.warning(f"Tag retrieval failed: Slug '{slug}' not found", extra=log_extra)
            return DRFResponse({"detail": "Tag does not exist"}, status=HTTP_404_NOT_FOUND)

        questions = Question.objects.filter(tag=tag)
        return DRFResponse(
            {
                "tag": TagDetailSerializer(tag).data,
                "questions": QuestionListSerializer(questions, many=True).data,
            },
            status=HTTP_200_OK,
        )