from rest_framework import routers

from .views import UserListRetrieveViewSet


router = routers.SimpleRouter()

router.register('users', UserListRetrieveViewSet)

urlpatterns = router.urls