from rest_framework import viewsets, mixins

from .models import User
from .serializers import UserSerializer


# User list, retrieve
class UserListRetrieveViewSet(viewsets.GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer


# User destroy