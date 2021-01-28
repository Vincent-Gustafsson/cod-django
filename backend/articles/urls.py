from django.urls import path

from rest_framework import routers

from .views import (ArticleViewSet, CommentViewSet, LikeArticleView,
                    UnlikeArticleView, UpvoteCommentView, DeleteCommentVoteView,
                    SaveArticleView)


router = routers.SimpleRouter()


router.register('articles/', ArticleViewSet)
router.register('comments/', CommentViewSet)

urlpatterns = [
    path(
        'articles/<int:pk>/like/',
        LikeArticleView.as_view(),
        name='article-like'
    ),
    path(
        'articles/<int:pk>/unlike/',
        UnlikeArticleView.as_view(),
        name='article-unlike'
    ),

    path(
        'comments/<int:pk>/vote/',
        UpvoteCommentView.as_view(),
        name='comment-vote'
    ),
    path(
        'comments/<int:pk>/vote/delete',
        DeleteCommentVoteView.as_view(),
        name='comment-vote-delete'
    ),

    path(
        'articles/<int:pk>/save/',
        SaveArticleView.as_view(),
        name='article-save'
    ),
] + router.urls
