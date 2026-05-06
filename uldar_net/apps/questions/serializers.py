from rest_framework import serializers

from apps.questions.models import Question
from apps.questions.utils import generate_unique_slug


class QuestionBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionCreateSerializer(QuestionBaseSerializer):
    class Meta:
        model = Question
        fields = ["id", "title", "description", "tag"]
        extra_kwargs = {
            "description": {"required": False},
            "tag": {"required": False},
        }

class QuestionDetailSerializer(QuestionBaseSerializer):
    class Meta:
        model = Question
        fields = ["id", "title", "description", "slug", "tag", "author", "created_at", "is_active"]

class QuestionListSerializer(QuestionBaseSerializer):
    class Meta:
        model = Question
        fields = ["id", "title", "description", "slug", "tag", "author", "is_active", "created_at"]

class QuestionUpdateSerializer(QuestionBaseSerializer):
    class Meta:
        model = Question
        fields = ["id", "title", "description", "tag", "is_active"]

    def update(self, instance, validated_data):
        if "title" in validated_data:
            instance.slug = generate_unique_slug(validated_data["title"])
        return super().update(instance, validated_data)