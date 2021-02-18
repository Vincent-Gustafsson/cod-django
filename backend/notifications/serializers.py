from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    object_url = serializers.SerializerMethodField()
    sender_url = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'sender_url', 'object_url', 'preview_text', 'seen', 'created_at')

    def get_object_url(self, obj):
        if obj.article:
            return obj.article.get_absolute_url()
        elif obj.comment:
            return obj.comment.get_absolute_url()
        elif obj.user:
            return obj.user.get_absolute_url()

    def get_sender_url(self, obj):
        return obj.sender.get_absolute_url()
