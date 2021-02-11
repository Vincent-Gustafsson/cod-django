from django.contrib.auth import get_user_model
from django.utils.text import Truncator

from rest_framework import serializers

from ..models import Tag, Article


User = get_user_model()


class FeedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name', 'slug',)


class ArticleUserFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'slug', 'avatar',)


class ArticleFeedSerializer(serializers.ModelSerializer):
    user = ArticleUserFeedSerializer()
    content = serializers.SerializerMethodField()

    tags = serializers.SlugRelatedField(
        many=True,
        required=False,
        slug_field='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Article
        fields = ('title', 'slug', 'tags', 'content', 'likes_count', 'created_at',
                  'special_likes_count', 'comments_count', 'user', 'thumbnail')

    def get_content(self, obj):
        """
        Truncates the content to 40 words
        and then adds '...' to the end.
        """
        return Truncator(obj.content).words(40)


class FollowedTagsSerializer(serializers.Serializer):
    followed_tags = serializers.SerializerMethodField()

    def get_followed_tags(self, obj):
        user = self.context['request'].user
        tags = user.followed_tags.all()
        return FeedTagSerializer(tags, many=True).data


class FollowedUsersSerializer(serializers.Serializer):
    followed_users = serializers.SerializerMethodField()

    def get_followed_users(self, obj):
        user = self.context['request'].user
        following = user.following.values_list('user_followed', flat=True)
        users = User.objects.filter(id__in=following)
        return ArticleUserFeedSerializer(users, many=True).data
