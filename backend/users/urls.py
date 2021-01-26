from django.urls import path

from rest_framework import routers

from .views import (UserListRetrieveViewSet,
                    UserDestroyView,
                    UserProfileUpdateView)


router = routers.SimpleRouter()

router.register('users', UserListRetrieveViewSet)

urlpatterns = [
    path('users/delete/', UserDestroyView.as_view(), name='user-delete'),
    path('users/profile/', UserProfileUpdateView.as_view(), name="user-profile-update")
]

urlpatterns += router.urls
