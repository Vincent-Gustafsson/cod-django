from django.urls import path

from rest_framework import routers

from .views import (UserListRetrieveViewSet,
                    UserDestroyView,
                    UserProfileUpdateView)


router = routers.SimpleRouter()

router.register('users', UserListRetrieveViewSet, basename='User')

urlpatterns = [
    # These two routes are kind of like "settings"
    # Delete user
    path('users/delete/', UserDestroyView.as_view(), name='user-delete'),
    # Update profile (update view for display_name, description and avatar)
    path('users/profile/', UserProfileUpdateView.as_view(), name="user-profile-update")
] + router.urls
