from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import ValidationError

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
    reported_by_slug = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ('id', 'message', 'created_at', 'reported_obj',
                  'reported_by', 'reported_by_display_name', 'reported_by_slug',
                  'article', 'comment', 'user', 'reason', 'moderated')

        read_only_fields = ('reported_by',)

        # Repetition here, could've used "fromkeys()" but this is simpler to understand. KISS.
        extra_kwargs = {
            'article': {'write_only': True},
            'comment': {'write_only': True},
            'user': {'write_only': True}
        }

    def get_reported_obj(self, obj):
        if obj.article:
            return ReportedArticleSerializer(obj.article).data

        elif obj.comment:
            return ReportedCommentSerializer(obj.comment).data

        elif obj.user:
            return ReportedUserSerializer(obj.user).data

    def get_reported_by_slug(self, obj):
        return obj.reported_by.slug

    def get_reported_by_display_name(self, obj):
        return obj.reported_by.display_name

    def create(self, validated_data):
        article = validated_data.pop('article', None)
        comment = validated_data.pop('comment', None)
        user = validated_data.pop('user', None)

        # 5 is the reason "OTHER"
        reason = validated_data.pop('reason', 5)

        reported_by = self.context['request'].user

        if article:
            comment = user = None
            if reported_by == article.user:
                raise ValidationError({'details': 'Can\'t report your own article.'})

        elif comment:
            article = user = None
            if reported_by == comment.user:
                raise ValidationError({'details': 'Can\'t report your own comment.'})

        elif user:
            article = comment = None
            if reported_by == user:
                raise ValidationError({'details': 'Can\'t report yourself.'})

        else:
            raise ValidationError({'details': 'Can\'t report multiple, or no, objects.'})

        report = Report.objects.create(
            message=validated_data.pop('message', None),
            reason=reason,
            article=article,
            comment=comment,
            user=user,
            reported_by=reported_by
        )

        return report
