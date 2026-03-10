from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet

from apps.comments.models import Comments
from apps.comments.serializers import CommentCreateSerializer, CommentListSerializer, CommentUpdateSerializer


comment_update_response = inline_serializer(
    name="CommentUpdateResponse",
    fields={
        "details": serializers.CharField(),
        "data": CommentListSerializer(),
    },
)

error_response = inline_serializer(
    name="CommentErrorResponse",
    fields={"detail": serializers.CharField()},
)


@extend_schema_view(
    list=extend_schema(
        tags=["Comments"],
        summary="List all comments",
        responses={200: CommentListSerializer(many=True)},
    ),
    create_comment=extend_schema(
        tags=["Comments"],
        summary="Create a comment",
        request=CommentCreateSerializer,
        responses={201: CommentListSerializer},
    ),
    update_comment=extend_schema(
        tags=["Comments"],
        summary="Update comment by id",
        request=CommentUpdateSerializer,
        responses={200: comment_update_response, 403: error_response, 404: error_response},
    ),
    list_comments_by_author=extend_schema(
        tags=["Comments"],
        summary="List comments by author",
        parameters=[
            OpenApiParameter(
                name="author",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Author user ID",
            )
        ],
        responses={200: CommentListSerializer(many=True), 400: error_response},
    ),
)
class CommentViewSet(ViewSet):
    queryset = Comments.objects.all()

    def list(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        comments = Comments.objects.all()
        serializer = CommentListSerializer(comments, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)

    @action(url_path="create", detail=False, permission_classes=[IsAuthenticated], methods=["POST"])
    def create_comment(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = Comments.objects.create(
            text=serializer.validated_data["text"],
            author=request.user,
            question=serializer.validated_data["question"],
        )

        return DRFResponse(CommentListSerializer(comment).data, status=HTTP_201_CREATED)

    @action(methods=["PATCH"], permission_classes=[IsAuthenticated], url_path="update", detail=True)
    def update_comment(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        try:
            comment = Comments.objects.get(pk=kwargs.get("pk"))
        except Comments.DoesNotExist:
            return DRFResponse({"detail": "The comment does not exist"}, status=HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            return DRFResponse({"detail": "You can edit only your comment"}, status=HTTP_403_FORBIDDEN)

        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return DRFResponse(
            {
                "details": "The comment successfully updated",
                "data": CommentListSerializer(comment).data,
            },
            status=HTTP_200_OK,
        )

    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list_by_author", detail=False)
    def list_comments_by_author(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        author_id = request.query_params.get("author")
        if not author_id:
            return DRFResponse({"detail": "author is required"}, status=HTTP_400_BAD_REQUEST)

        comments = Comments.objects.filter(author=author_id)
        serializer = CommentListSerializer(comments, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)