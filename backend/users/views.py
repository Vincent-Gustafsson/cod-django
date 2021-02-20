from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, mixins, generics, exceptions, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer, UserProfileSerializer


class UserListRetrieveViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin):
    """ Handles listing, details & creation of users. """
    serializer_class = UserSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Filters the queryset by:
            q - filters users by username and display name, icontains (case insensitve, contains)
        """
        queryset = User.objects.all()
        q = self.request.query_params.get('q', None)

        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | Q(display_name__icontains=q)
            )

        return queryset


class UserDestroyView(generics.DestroyAPIView):
    """ Handles the deletion of users. """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.id)
            return instance
        except User.DoesNotExist:
            raise exceptions.NotFound()


class UserProfileUpdateView(generics.UpdateAPIView):
    """ User profile view. """
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.id)
            return instance
        except User.DoesNotExist:
            raise exceptions.NotFound()


class FollowUserView(views.APIView):
    """ Handles following of users. """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        user = request.user
        user_to_follow = get_object_or_404(User, slug=slug)

        is_self = (user == user_to_follow)

        if not is_self:
            if not user.is_already_following(user_to_follow):
                user.follow(user_to_follow)
                return Response(
                    {'details': 'Follow successful.'},
                    status=status.HTTP_201_CREATED
                )

            else:
                return Response(
                    {'details': 'Already following.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'Can\'t follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UnfollowUserView(views.APIView):
    """ Handles unfollowing of users. """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, slug):
        user = request.user
        user_to_unfollow = get_object_or_404(User, slug=slug)

        is_self = (user == user_to_unfollow)

        if not is_self:
            if user.unfollow(user_to_unfollow):
                return Response(status=status.HTTP_204_NO_CONTENT)

            else:
                return Response(
                    {'details': 'You\'re not following that person.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'Can\'t unfollow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )
