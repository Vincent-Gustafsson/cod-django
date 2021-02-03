from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Tag, Article, Comment


User = get_user_model()


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'slug', 'avatar',)
        read_only_fields = ('display_name', 'slug', 'avatar',)


class CommentSerializer(serializers.ModelSerializer):
    children = RecursiveCommentSerializer(many=True, read_only=True)
    user = CommentUserSerializer(read_only=True)

    class Meta:
        model = Comment
        # TODO parent, article fields may be unneeded
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
    tags = serializers.SlugRelatedField(many=True, required=False, slug_field='slug', queryset=Tag.objects.all())

    comments = CommentSerializer(many=True, read_only=True)

    likes_count = serializers.ReadOnlyField()
    special_likes_count = serializers.ReadOnlyField()
    saved_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('user', 'slug',)
        lookup_field = 'slug'

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        tags = validated_data.pop('tags', None)

        article = Article.objects.create(**validated_data)

        if tags:
            for tag in tags:
                article.tags.add(tag)

        return article
