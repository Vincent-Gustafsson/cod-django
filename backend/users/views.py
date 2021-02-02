from django.db.models import Q

from rest_framework import viewsets, mixins, generics, exceptions

from .models import User
from .serializers import UserSerializer, UserProfileSerializer


# User list, retrieve
class UserListRetrieveViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.RetrieveModelMixin):

    serializer_class = UserSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = User.objects.all()
        # q = query / search
        q = self.request.query_params.get('q', None)

        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) | Q(display_name__icontains=q)
            )

        return queryset


class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.id)
            return instance
        except User.DoesNotExist:
            raise exceptions.NotFound()


class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.id)
            return instance
        except User.DoesNotExist:
            raise exceptions.NotFound()
