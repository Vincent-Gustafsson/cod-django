from rest_framework import routers, urlpatterns

from .views import ArticleViewSet, CommentViewSet


router = routers.SimpleRouter()


router.register('articles/', ArticleViewSet)
router.register('comments/', CommentViewSet)

urlpatterns = router.urls
