from django.urls import path

from rest_framework import routers

from .views import ArticleViewSet, CommentViewSet, LikeArticleView, UnlikeArticleView


router = routers.SimpleRouter()


router.register('articles/', ArticleViewSet)
router.register('comments/', CommentViewSet)

urlpatterns = [
    path('article/<int:pk>/like/', LikeArticleView.as_view(), name='article-like'),
    path('article/<int:pk>/unlike/', UnlikeArticleView.as_view(), name='article-unlike'),
] + router.urls
