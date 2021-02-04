from django.urls import path

from rest_framework import routers

from .views import (UserListRetrieveViewSet,
                    UserDestroyView,
                    UserProfileUpdateView,
                    FollowUserView,
                    UnfollowUserView)


router = routers.SimpleRouter()

router.register('users', UserListRetrieveViewSet, basename='user')

urlpatterns = [
    # These two routes are kind of like "settings"
    # Delete user
    path('users/delete/', UserDestroyView.as_view(), name='user-delete'),
    # Update profile (update view for display_name, description and avatar)
    path('users/profile/', UserProfileUpdateView.as_view(), name="user-profile-update"),

    path('users/<str:slug>/follow', FollowUserView.as_view(), name="user-follow"),
    path('users/<str:slug>/unfollow', UnfollowUserView.as_view(), name="user-unfollow")
] + router.urls
