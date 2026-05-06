from rest_framework import serializers

from apps.comments.models import Comments


class CommentBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"


class CommentListSerializer(CommentBaseSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = Comments
        fields = ["id", "author", "question", "text", "author_email", "created_at", "updated_at"]


class CommentCreateSerializer(CommentBaseSerializer):
    class Meta:
        model = Comments
        fields = ["id", "question", "text"]
        extra_kwargs = {
            "text": {"required": True, "max_length": Comments.MAX_TEXT_LENGTH},
        }


class NestedCommentCreateSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=Comments.MAX_TEXT_LENGTH)


class CommentUpdateSerializer(CommentBaseSerializer):
    class Meta:
        model = Comments
        fields = ["text"]
