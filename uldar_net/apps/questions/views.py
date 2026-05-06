import uuid

from django.utils.text import slugify
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet, ModelViewSet

from apps.comments.models import Comments
from apps.comments.serializers import CommentListSerializer, NestedCommentCreateSerializer
from apps.questions.models import Question
from apps.questions.serializers import (
    QuestionCreateSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateSerializer,
)
# Permissions
from apps.common.permissions import IsAuthorOrReadOnly


question_retrieve_response = inline_serializer(
    name="QuestionRetrieveResponse",
    fields={
        "question": QuestionDetailSerializer(),
        "comments": CommentListSerializer(many=True),
    },
)

question_update_response = inline_serializer(
    name="QuestionUpdateResponse",
    fields={
        "details": serializers.CharField(),
        "data": QuestionUpdateSerializer(),
    },
)

error_response = inline_serializer(
    name="QuestionErrorResponse",
    fields={"detail": serializers.CharField()},
)

validation_error_response = inline_serializer(
    name="QuestionValidationErrorResponse",
    fields={
        "title": serializers.ListField(child=serializers.CharField(), required=False),
        "description": serializers.ListField(child=serializers.CharField(), required=False),
        "tag": serializers.ListField(child=serializers.CharField(), required=False),
        "text": serializers.ListField(child=serializers.CharField(), required=False),
        "detail": serializers.CharField(required=False),
    },
)


@extend_schema_view(
    list_questions=extend_schema(
        tags=["Questions"],
        summary="List all questions",
        description=(
            "Returns a list of all questions. Authentication is not required."
        ),
        responses={
            200: OpenApiResponse(
                response=QuestionListSerializer(many=True),
                description="Questions were returned successfully.",
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
                "List questions response example",
                response_only=True,
                status_codes=["200"],
                value=[
                    {
                        "id": 1,
                        "title": "How to use serializers in Django?",
                        "slug": "how-to-use-serializers-in-django",
                    },
                    {
                        "id": 2,
                        "title": "How to connect JWT auth?",
                        "slug": "how-to-connect-jwt-auth",
                    },
                ],
            ),
        ],
    ),
    retrieve_question=extend_schema(
        tags=["Questions"],
        summary="Retrieve question by slug",
        description=(
            "Returns detailed information about a single question and all comments related to it. "
            "Authentication is not required."
        ),
        responses={
            200: OpenApiResponse(
                response=question_retrieve_response,
                description="Question and related comments were returned successfully.",
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
                description="Question was not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Retrieve question response example",
                response_only=True,
                status_codes=["200"],
                value={
                    "question": {
                        "id": 1,
                        "title": "How to use serializers in Django?",
                        "description": "I want to understand why serializers are needed.",
                        "slug": "how-to-use-serializers-in-django",
                    },
                    "comments": [
                        {
                            "id": 1,
                            "text": "They validate and transform data.",
                        }
                    ],
                },
            ),
            OpenApiExample(
                "Question not found example",
                response_only=True,
                status_codes=["404"],
                value={
                    "detail": "Question does not exist"
                },
            ),
        ],
    ),
    destroy_question=extend_schema(
        tags=["Questions"],
        summary="Delete question by slug",
        description=(
            "Deletes a question by its slug. Authentication is required. "
            "Only the author of the question can delete it."
        ),
        responses={
            204: OpenApiResponse(
                description="Question was deleted successfully.",
            ),
            400: OpenApiResponse(
                response=validation_error_response,
                description="Bad request.",
            ),
            401: OpenApiResponse(
                response=error_response,
                description="Authentication credentials were not provided or are invalid.",
            ),
            403: OpenApiResponse(
                response=error_response,
                description="User is not allowed to delete this question.",
            ),
            404: OpenApiResponse(
                response=error_response,
                description="Question was not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Delete forbidden example",
                response_only=True,
                status_codes=["403"],
                value={
                    "detail": "You are not the author of this question"
                },
            ),
        ],
    ),
    create_question=extend_schema(
        tags=["Questions"],
        summary="Create a new question",
        description=(
            "Creates a new question. Authentication is required. "
            "The request body must contain the fields required by the question creation serializer."
        ),
        request=QuestionCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=QuestionDetailSerializer,
                description="Question was created successfully.",
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
                "Create question request example",
                request_only=True,
                value={
                    "title": "How to use serializers in Django?",
                    "description": "Please explain with a simple example.",
                    "tag": [1, 2],
                },
            ),
            OpenApiExample(
                "Create question response example",
                response_only=True,
                status_codes=["201"],
                value={
                    "id": 1,
                    "title": "How to use serializers in Django?",
                    "description": "Please explain with a simple example.",
                    "slug": "how-to-use-serializers-in-django",
                },
            ),
        ],
    ),
    update_question=extend_schema(
        tags=["Questions"],
        summary="Update question by slug",
        description=(
            "Partially updates an existing question by its slug. Authentication is required. "
            "Only the author of the question can update it. "
            "The request body may contain one or more editable fields."
        ),
        request=QuestionUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=question_update_response,
                description="Question was updated successfully.",
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
                description="User is not allowed to update this question.",
            ),
            404: OpenApiResponse(
                response=error_response,
                description="Question was not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Update question request example",
                request_only=True,
                value={
                    "title": "How do serializers work in Django REST Framework?"
                },
            ),
            OpenApiExample(
                "Update question response example",
                response_only=True,
                status_codes=["200"],
                value={
                    "details": "The question successfully updated",
                    "data": {
                        "title": "How do serializers work in Django REST Framework?"
                    },
                },
            ),
            OpenApiExample(
                "Update forbidden example",
                response_only=True,
                status_codes=["403"],
                value={
                    "detail": "You can edit only your question"
                },
            ),
        ],
    ),
    create_comment=extend_schema(
        tags=["Questions"],
        summary="Create comment for a question",
        description=(
            "Creates a new comment for the selected question. Authentication is required. "
            "The request body must contain the comment text."
        ),
        request=NestedCommentCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=CommentListSerializer,
                description="Comment was created successfully.",
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
                description="Question was not found.",
            ),
            429: OpenApiResponse(
                response=error_response,
                description="Too many requests.",
            ),
        },
        examples=[
            OpenApiExample(
                "Create comment request example",
                request_only=True,
                value={
                    "text": "You should use serializers for validation and transformation."
                },
            ),
            OpenApiExample(
                "Create comment response example",
                response_only=True,
                status_codes=["201"],
                value={
                    "id": 1,
                    "text": "You should use serializers for validation and transformation.",
                },
            ),
        ],
    ),
    list_questions_by_author=extend_schema(
        tags=["Questions"],
        summary="List questions by author",
        description=(
            "Returns a list of questions created by a specific author. "
            "Authentication is not required. "
            "The author must be passed as a required query parameter."
        ),
        parameters=[
            OpenApiParameter(
                name="author",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Author user ID",
            )
        ],
        responses={
            200: OpenApiResponse(
                response=QuestionListSerializer(many=True),
                description="Questions by author were returned successfully.",
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
                "List questions by author response example",
                response_only=True,
                status_codes=["200"],
                value=[
                    {
                        "id": 3,
                        "title": "How to create JWT login?",
                        "slug": "how-to-create-jwt-login",
                    }
                ],
            ),
        ],
    ),
)
class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    lookup_field = "slug"

    permission_classes = [IsAuthorOrReadOnly]

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list", detail=False)
    def list_questions(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        questions = Question.objects.all()
        serializer = QuestionListSerializer(questions, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="retrieve", detail=True)
    def retrieve_question(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        slug = kwargs.get("slug") or kwargs.get("pk") or slug
        try:
            question = Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            return DRFResponse({"detail": "Question does not exist"}, status=HTTP_404_NOT_FOUND)

        comments = Comments.objects.filter(question=question)
        return DRFResponse(
            {
                "question": QuestionDetailSerializer(question).data,
                "comments": CommentListSerializer(comments, many=True).data,
            },
            status=HTTP_200_OK,
        )

    @action(methods=["DELETE"], permission_classes=[IsAuthenticated], url_path="destroy", detail=True)
    def destroy_question(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        slug = kwargs.get("slug") or kwargs.get("pk") or slug
        try:
            question = Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            return DRFResponse({"detail": "Question does not exist"}, status=HTTP_404_NOT_FOUND)

        if question.author != request.user:
            return DRFResponse({"detail": "You are not the author of this question"}, status=HTTP_403_FORBIDDEN)

        question.delete()
        return DRFResponse(status=HTTP_204_NO_CONTENT)

    @action(methods=["POST"], permission_classes=[IsAuthenticated], url_path="create", detail=False)
    def create_question(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        base_slug = slugify(data["title"])
        slug = base_slug
        while Question.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        question = Question.objects.create(
            title=data["title"],
            description=data.get("description"),
            slug=slug,
            author=request.user,
        )
        question.tag.set(data.get("tag", []))

        return DRFResponse(QuestionDetailSerializer(question).data, status=HTTP_201_CREATED)

    @action(methods=["PATCH"], permission_classes=[IsAuthenticated], url_path="update", detail=True)
    def update_question(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        slug = kwargs.get("slug") or kwargs.get("pk") or slug
        try:
            question = Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            return DRFResponse({"detail": "The question does not exist"}, status=HTTP_404_NOT_FOUND)

        if question.author != request.user:
            return DRFResponse({"detail": "You can edit only your question"}, status=HTTP_403_FORBIDDEN)

        serializer = QuestionUpdateSerializer(question, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            {
                "details": "The question successfully updated",
                "data": serializer.data,
            },
            status=HTTP_200_OK,
        )

    @action(methods=["POST"], permission_classes=[IsAuthenticated], url_path="create_comment", detail=True)
    def create_comment(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
        slug = kwargs.get("slug") or kwargs.get("pk") or slug
        try:
            question = Question.objects.get(slug=slug)
        except Question.DoesNotExist:
            return DRFResponse({"detail": "Question does not exist"}, status=HTTP_404_NOT_FOUND)

        serializer = NestedCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comments.objects.create(
            text=serializer.validated_data["text"],
            author=request.user,
            question=question,
        )

        return DRFResponse(CommentListSerializer(comment).data, status=HTTP_201_CREATED)

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list_by_author", detail=False)
    def list_questions_by_author(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        author_id = request.query_params.get("author")
        questions = Question.objects.filter(author=author_id)
        serializer = QuestionListSerializer(questions, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)