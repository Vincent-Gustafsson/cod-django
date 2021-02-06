from rest_framework import routers, urlpatterns

from .views import ReportViewSet


router = routers.SimpleRouter()

router.register('reports', ReportViewSet, basename='report')

urlpatterns = router.urls
