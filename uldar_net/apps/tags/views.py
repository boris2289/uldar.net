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


@extend_schema_view(
    list_tags=extend_schema(
        tags=["Tags"],
        summary="List all tags",
        description=(
            "Returns a list of all tags. Authentication is not required, "
            "but authenticated and unauthenticated users may both access this endpoint."
        ),
        responses={
            200: OpenApiResponse(
                response=TagListSerializer(many=True),
                description="Tags were returned successfully.",
            ),
            400: OpenApiResponse(
                response=validation_error_response,
                description="Bad request.",
            ),
            401: OpenApiResponse(
                response=error_response,
                description="Unauthorized.",
            ),
            403: OpenApiResponse(
                response=error_response,
                description="Forbidden.",
            ),
            404: OpenApiResponse(
                response=error_response,
                description="Not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
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
    ),
    create_tag=extend_schema(
        tags=["Tags"],
        summary="Create a new tag",
        description=(
            "Creates a new tag using the provided name. Authentication is required. "
            "If a tag with the same name already exists, the existing tag is returned instead of creating a duplicate."
        ),
        request=TagCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=TagDetailSerializer,
                description="Tag was created successfully.",
            ),
            400: OpenApiResponse(
                response=validation_error_response,
                description="Validation error.",
            ),
            401: OpenApiResponse(
                response=error_response,
                description="Authentication credentials were not provided or are invalid.",
            ),
            403: OpenApiResponse(
                response=error_response,
                description="Forbidden.",
            ),
            404: OpenApiResponse(
                response=error_response,
                description="Not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Create tag request example",
                request_only=True,
                value={
                    "name": "Machine Learning"
                },
            ),
            OpenApiExample(
                "Create tag response example",
                response_only=True,
                status_codes=["201"],
                value={
                    "id": 3,
                    "name": "Machine Learning",
                    "slug": "machine-learning"
                },
            ),
        ],
    ),
    retrieve_tag=extend_schema(
        tags=["Tags"],
        summary="Retrieve tag by slug",
        description=(
            "Returns detailed information about a tag and the list of questions linked to it. "
            "Authentication is not required."
        ),
        responses={
            200: OpenApiResponse(
                response=tag_retrieve_response,
                description="Tag and related questions were returned successfully.",
            ),
            400: OpenApiResponse(
                response=validation_error_response,
                description="Bad request.",
            ),
            401: OpenApiResponse(
                response=error_response,
                description="Unauthorized.",
            ),
            403: OpenApiResponse(
                response=error_response,
                description="Forbidden.",
            ),
            404: OpenApiResponse(
                response=error_response,
                description="Tag was not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Retrieve tag response example",
                response_only=True,
                status_codes=["200"],
                value={
                    "tag": {
                        "id": 1,
                        "name": "Django",
                        "slug": "django"
                    },
                    "questions": [
                        {
                            "id": 10,
                            "title": "How to use serializers?",
                            "slug": "how-to-use-serializers"
                        }
                    ]
                },
            ),
            OpenApiExample(
                "Retrieve tag not found example",
                response_only=True,
                status_codes=["404"],
                value={
                    "detail": "Tag does not exist"
                },
            ),
        ],
    ),
)
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