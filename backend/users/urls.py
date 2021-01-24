import django
from django.urls import path

from rest_framework import routers

from .views import UserListRetrieveViewSet, UserDestroyView


router = routers.SimpleRouter()

router.register('users', UserListRetrieveViewSet)

urlpatterns = [
    # TODO FIX ROUTE NAME
    path('userstwo/', UserDestroyView.as_view(), name='user-delete'),
]

urlpatterns += router.urls
