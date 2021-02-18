from django.urls import path

from .views import ListNotificationsView, MarkAllNotifications, MarkNotification

urlpatterns = [
    path('notifications/', ListNotificationsView.as_view(), name='notification-list'),
    path('notifications/mark_all/', MarkAllNotifications.as_view(), name='notification-mark-all'),
    path('notifications/mark/<int:pk>/', MarkNotification.as_view(), name='notification-mark'),
]
