from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Article, Comment


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'body', 'user', 'article', 'score', 'parent', 'children', 'created_at',)
        read_only_fields = ('user',)

    def validate(self, data):
        if data.get('parent'):
            if not data['article'].id == data['parent'].article.id:
                raise ValidationError("Parent comment must have the same article id")

            return data

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        comment = Comment.objects.create(**validated_data)
        return comment


class ArticleSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    likes_count = serializers.ReadOnlyField()
    special_likes_count = serializers.ReadOnlyField()
    saved_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user', 'slug')
        lookup_field = 'slug'

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        article = Article.objects.create(**validated_data)
        return article
