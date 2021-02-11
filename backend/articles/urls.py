from django.urls import path

from rest_framework import routers

from .views import (ArticleViewSet, CommentViewSet, LikeArticleView,
                    UnlikeArticleView, UpvoteCommentView, DeleteCommentVoteView,
                    SaveArticleView, UnsaveArticleView, ArticleFeedView, FollowTagView,
                    UnfollowTagView)


router = routers.SimpleRouter()


router.register('articles', ArticleViewSet, basename='article')
router.register('comments', CommentViewSet)

urlpatterns = [
    path('feed', ArticleFeedView.as_view(), name='article-feed'),

    path('tags/<str:slug>/follow', FollowTagView.as_view(), name='tag-follow'),
    path('tags/<str:slug>/unfollow', UnfollowTagView.as_view(), name='tag-unfollow'),

    path(
        'articles/<str:slug>/like/',
        LikeArticleView.as_view(),
        name='article-like'
    ),
    path(
        'articles/<str:slug>/unlike/',
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
        'articles/<str:slug>/save/',
        SaveArticleView.as_view(),
        name='article-save'
    ),
    path(
        'articles/<str:slug>/unsave/',
        UnsaveArticleView.as_view(),
        name='article-unsave'
    ),
] + router.urls
