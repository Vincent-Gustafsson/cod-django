from rest_framework import status, generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import NotificationSerializer
from .pagination import NotificationsPagination


class ListNotificationsView(generics.ListAPIView):
    """ Returns all the user's notification """
    serializer_class = NotificationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = NotificationsPagination

    def get_queryset(self):
        return self.request.user.get_all_notifications().order_by('seen')

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkAllNotifications(views.APIView):
    """ Marks all the user's notifications as seen """
    def post(self, request):
        queryset = request.user.get_all_notifications().filter(seen=False)

        try:
            queryset.update(seen=True)

        except Exception:
            return Response(
                {'details': 'Couldn\'t mark all notifications as seen.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_200_OK)


class MarkNotification(views.APIView):
    """ Marks the notification as seen """
    def post(self, request):
        notification_id = request.data.get('id', None)

        if notification_id:
            try:
                notification = request.user.get_all_notifications().get(pk=notification_id)
                notification.seen = True
                notification.save()

            except Exception:
                return Response(
                    {'details': 'Couldn\'t mark all the notification as seen.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(status=status.HTTP_200_OK)

        return Response(
            {'details': 'Coudln\'t find the notification.'},
            status=status.HTTP_400_BAD_REQUEST
        )
