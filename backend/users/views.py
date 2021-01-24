from rest_framework import viewsets, mixins, generics, exceptions

from .models import User
from .serializers import UserSerializer


# User list, retrieve
class UserListRetrieveViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        try:
            instance = self.queryset.get(pk=self.request.user.id)
            return instance
        except User.DoesNotExist:
            raise exceptions.NotFound()


# TODO UPDATE PROFILE VIEW
