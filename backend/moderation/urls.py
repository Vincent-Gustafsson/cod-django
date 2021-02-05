from rest_framework import routers, urlpatterns

from .views import ArticleReportViewSet


router = routers.SimpleRouter()

router.register('article-reports', ArticleReportViewSet, basename='Report')

urlpatterns = router.urls
