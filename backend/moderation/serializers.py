from django.contrib.auth import get_user_model

from rest_framework import serializers

from articles.models import Article, Comment

from .models import Report


User = get_user_model()


class ReportedArticleSerializer(serializers.ModelSerializer):
    user_slug = serializers.SerializerMethodField()
    user_display_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('slug', 'reports_count', 'user_slug', 'user_display_name',)

    def get_user_slug(self, obj):
        return obj.user.slug

    def get_user_display_name(self, obj):
        return obj.user.display_name


class ReportedCommentSerializer(serializers.ModelSerializer):
    article_slug = serializers.SerializerMethodField()
    user_slug = serializers.SerializerMethodField()
    user_display_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('article_slug', 'reports_count', 'user_slug', 'user_display_name',)

    def get_article_slug(self, obj):
        return obj.article.slug

    def get_user_slug(self, obj):
        return obj.user.slug

    def get_user_display_name(self, obj):
        return obj.user.display_name


class ReportedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('slug', 'display_name', 'reports_count',)


class ReportSerializer(serializers.ModelSerializer):
    reported_obj = serializers.SerializerMethodField()
    reported_by_display_name = serializers.SerializerMethodField()
    reported_by = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ('id', 'message', 'created_at', 'reported_obj',
                  'reported_by', 'reported_by_display_name',)

    def get_reported_obj(self, obj):
        if obj.article:
            return ReportedArticleSerializer(obj.article).data

        elif obj.comment:
            return ReportedCommentSerializer(obj.comment).data

        elif obj.user:
            return ReportedUserSerializer(obj.user).data

    def get_reported_by(self, obj):
        return obj.reported_by.slug

    def get_reported_by_display_name(self, obj):
        return obj.reported_by.display_name
