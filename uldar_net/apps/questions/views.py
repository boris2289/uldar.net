import uuid

from django.utils.text import slugify
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet

from apps.comments.models import Comments
from apps.comments.serializers import CommentListSerializer, NestedCommentCreateSerializer
from apps.questions.models import Question
from apps.questions.serializers import QuestionCreateSerializer, QuestionDetailSerializer, QuestionListSerializer, QuestionUpdateSerializer


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


@extend_schema_view(
    list_questions=extend_schema(
        tags=["Questions"],
        summary="List all questions",
        responses={200: QuestionListSerializer(many=True)},
    ),
    retrieve_question=extend_schema(
        tags=["Questions"],
        summary="Retrieve question by slug",
        responses={200: question_retrieve_response, 404: error_response},
    ),
    destroy_question=extend_schema(
        tags=["Questions"],
        summary="Delete question by slug",
        responses={204: None, 403: error_response, 404: error_response},
    ),
    create_question=extend_schema(
        tags=["Questions"],
        summary="Create a question",
        request=QuestionCreateSerializer,
        responses={201: QuestionDetailSerializer},
    ),
    update_question=extend_schema(
        tags=["Questions"],
        summary="Update question by slug",
        request=QuestionUpdateSerializer,
        responses={200: question_update_response, 403: error_response, 404: error_response},
    ),
    create_comment=extend_schema(
        tags=["Questions"],
        summary="Create comment for a question",
        request=NestedCommentCreateSerializer,
        responses={201: CommentListSerializer, 404: error_response},
    ),
    list_questions_by_author=extend_schema(
        tags=["Questions"],
        summary="List questions by author",
        parameters=[
            OpenApiParameter(
                name="author",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Author user ID",
            )
        ],
        responses={200: QuestionListSerializer(many=True)},
    ),
)
class QuestionViewSet(ViewSet):
    queryset = Question.objects.all()
    lookup_field = "slug"

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list", detail=False)
    def list_questions(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        questions = Question.objects.all()
        serializer = QuestionListSerializer(questions, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="retrieve", detail=True)
    def retrieve_question(self, request: DRFRequest, slug: str = None, *args, **kwargs) -> DRFResponse:
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