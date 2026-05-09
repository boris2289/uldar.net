

# Rest-Framework imports
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response as DRFResponse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet
from logging import getLogger

# DRF imports
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)

# Project imports
from apps.comments.models import Comments
from apps.comments.serializers import CommentCreateSerializer, CommentListSerializer, CommentUpdateSerializer
from apps.comments.schema import comment_schema
from apps.common.responses import ERROR_400, ERROR_401, ERROR_403, ERROR_404, ERROR_429, VALIDATION_400

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

validation_error_response = inline_serializer(
    name="CommentValidationErrorResponse",
    fields={
        "text": serializers.ListField(child=serializers.CharField(), required=False),
        "question": serializers.ListField(child=serializers.CharField(), required=False),
        "detail": serializers.CharField(required=False),
    },
)

logger = getLogger('django')


class CommentViewSet(ViewSet):
    queryset = Comments.objects.all()

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
        tags=["Comments"],
        summary="List all comments",
        description="Returns a list of all comments. Authentication is not required.",
        responses={
            200: OpenApiResponse(response=CommentListSerializer(many=True), description="Comments were returned successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "List comments response example",
                response_only=True,
                status_codes=["200"],
                value=[
                    {"id": 1, "text": "You should use serializers for validation."},
                    {"id": 2, "text": "JWT is useful for stateless authentication."},
                ],
            ),
        ],
    )
    
    
    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list", detail=False)
    def list_comments(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        comments = Comments.objects.all()
        serializer = CommentListSerializer(comments, many=True)
        return DRFResponse(serializer.data, status=HTTP_200_OK)
    
    
    @extend_schema(
        tags=["Comments"],
        summary="Create a new comment",
        description="Creates a new comment. Authentication is required.",
        request=CommentCreateSerializer,
        responses={
            201: OpenApiResponse(response=CommentListSerializer, description="Comment was created successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample(
                "Create comment request example",
                request_only=True,
                value={"text": "I think serializers are needed for validation and representation.", "question": 1},
            ),
            OpenApiExample(
                "Create comment response example",
                response_only=True,
                status_codes=["201"],
                value={"id": 1, "text": "I think serializers are needed for validation and representation."},
            ),
        ],
    )
    @action(url_path="create", detail=False, permission_classes=[IsAuthenticated], methods=["POST"])
    def create_comment(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        log_extra = self._get_log_context(request)
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            comment = Comments.objects.create(
                text=serializer.validated_data["text"],
                author=request.user,
                question=serializer.validated_data["question"],
            )

            return DRFResponse(CommentListSerializer(comment).data, status=HTTP_201_CREATED)
        except Exception as e:
            log_extra['error_detail'] = str(e)
            logger.warning("Creation of Comment failed", extra=log_extra)
            return DRFResponse({"detail": "Comment creation failed"}, status=500)
        
    @extend_schema(
        tags=["Comments"],
        summary="Update comment by id",
        description="Partially updates a comment by its id. Only the author can update it.",
        request=CommentUpdateSerializer,
        responses={
            200: OpenApiResponse(response=comment_update_response, description="Comment was updated successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample("Update comment request example", request_only=True, value={"text": "Updated comment text"}),
            OpenApiExample(
                "Update comment response example",
                response_only=True,
                status_codes=["200"],
                value={"details": "The comment successfully updated", "data": {"id": 1, "text": "Updated comment text"}},
            ),
            OpenApiExample("Update comment forbidden example", response_only=True, status_codes=["403"], value={"detail": "You can edit only your comment"}),
            OpenApiExample("Update comment not found example", response_only=True, status_codes=["404"], value={"detail": "The comment does not exist"}),
        ],
    )
    @action(methods=["PATCH"], permission_classes=[IsAuthenticated], url_path="update", detail=True)
    def update_comment(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        log_extra = self._get_log_context(request)
        try:
            comment = Comments.objects.get(pk=kwargs.get("pk"))
        except Comments.DoesNotExist:
            logger.warning("Update of Comment failed: Comment does not exist", extra=log_extra)
            return DRFResponse({"detail": "The comment does not exist"}, status=HTTP_404_NOT_FOUND)

        if comment.author != request.user:
            logger.warning("Update of Comment failed: Forbidden", extra=log_extra)
            return DRFResponse({"detail": "You can edit only your comment"}, status=HTTP_403_FORBIDDEN)

        serializer = CommentUpdateSerializer(comment, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Update of Comment is successful", extra=log_extra)
        return DRFResponse(
            {
                "details": "The comment successfully updated",
                "data": CommentListSerializer(comment).data,
            },
            status=HTTP_200_OK,
        )
    
    
    @extend_schema(
        tags=["Comments"],
        summary="List comments by author",
        description="Returns comments by a specific author. Pass author ID as a query parameter.",
        parameters=[
            OpenApiParameter(name="author", type=int, location=OpenApiParameter.QUERY, required=True, description="Author user ID")
        ],
        responses={
            200: OpenApiResponse(response=CommentListSerializer(many=True), description="Comments by author were returned successfully."),
            400: VALIDATION_400,
            401: ERROR_401,
            403: ERROR_403,
            404: ERROR_404,
            429: ERROR_429,
        },
        examples=[
            OpenApiExample("List comments by author response example", response_only=True, status_codes=["200"], value=[{"id": 3, "text": "This is my comment."}]),
            OpenApiExample("Author query param missing example", response_only=True, status_codes=["400"], value={"detail": "author is required"}),
        ],
    )
    @action(methods=["GET"], permission_classes=[AllowAny], url_path="list_by_author", detail=False)
    def list_comments_by_author(self, request: DRFRequest, *args, **kwargs) -> DRFResponse:
        author_id = request.query_params.get("author")
        log_extra = self._get_log_context(request)
        
        if not author_id:
            logger.warning('list_comments_by_author no author in request', extra=log_extra)
            return DRFResponse({"detail": "author is required"}, status=HTTP_400_BAD_REQUEST)

        comments = Comments.objects.filter(author=author_id)
        serializer = CommentListSerializer(comments, many=True)
        logger.info('list_comments_by_author successful')
        return DRFResponse(serializer.data, status=HTTP_200_OK)