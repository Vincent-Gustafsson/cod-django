from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import viewsets, views, status, generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Tag, Article, ArticleLike, Comment, CommentVote
from .serializers.article_serializers import ArticleSerializer, CommentSerializer
from .serializers.feed_serializers import (ArticleFeedSerializer,
                                           FollowedTagsSerializer,
                                           FollowedUsersSerializer)
from .permissions import IsOwnArticle
from .pagination import FeedPagination


class ArticleViewSet(viewsets.ModelViewSet):
    """ Handles creation, updating & deletion of articles. """
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnArticle,)
    lookup_field = 'slug'

    def get_queryset(self):
        """
        Filters the queryset by:
            title - title, icontains (case insensitve, contains)\n
            tag - tags, filters by tags, can filter by multiple tags,
            e.g. (\n
                localhost:8000/api/articles?tags=python&tags=backend\n
                Will return articles that has the tags 'python' and/or 'backend'.
            )
        """
        queryset = Article.objects.all()

        title = self.request.query_params.get('title', '')
        tags = self.request.query_params.getlist('tag', None)

        if title and tags:
            queryset = queryset.filter(
                Q(title__icontains=title) | Q(tags__slug__in=tags)
            )

        if title:
            queryset = queryset.filter(title__icontains=title)

        if tags:
            queryset = queryset.filter(tags__slug__in=tags)

        return queryset

    def get_object(self):
        """
        When the user tries to access a article,
        check if the article is a draft and if the owner is the requesting user. If not,
        keep going and do a normal get_object().
        """
        slug = self.kwargs.get('slug', None)
        user = self.request.user

        article = None

        try:
            article = Article.drafts.filter(user=user).get(slug=slug)

        except Exception:
            article = None

        if article:
            self.check_object_permissions(self.request, article)
            return article

        try:
            article = Article.objects.get(slug=slug)

        except Article.DoesNotExist:
            raise Http404

        self.check_object_permissions(self.request, article)
        return article


class DraftArticlesView(generics.ListAPIView):
    """ Returns all of the users draft articles. """
    queryset = Article.drafts.all()
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        """ Returns all of the users draft articles. """
        queryset = self.queryset.filter(user=request.user)
        serializer = ArticleSerializer(queryset, many=True)

        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ Handles creation, updating & deletion of comments. """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnArticle,)

    def destroy(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            comment.delete()
        except Http404:
            return Response(
                {'details': 'couldn\'t delete.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class SaveArticleView(views.APIView):
    """ Handles saving of articles. """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def post(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_has_saved = article.saves.filter(pk=user.id)

        if not is_owner:
            if not user_has_saved:
                user.saved_articles.add(article)

                return Response(
                    {'details': 'Saved article.'},
                    status=status.HTTP_200_OK
                )

            else:
                return Response(
                    {'details': 'You have already saved this article.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'You can\'t save your own article.'},
                status=status.HTTP_403_FORBIDDEN
            )


class UnsaveArticleView(views.APIView):
    """ Handles unsaving of articles. """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def delete(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_has_saved = article.saves.filter(pk=user.id)

        if not is_owner:
            if user_has_saved:
                user.saved_articles.remove(article)

                return Response(
                    status=status.HTTP_204_NO_CONTENT
                )

            else:
                return Response(
                    {'details': 'You must save before you can unsave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'You can\'t unsave your own post.'},
                status=status.HTTP_403_FORBIDDEN
            )


class LikeArticleView(views.APIView):
    """ Handles liking of articles. """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def post(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_liked = ArticleLike.objects.filter(user=user, special_like=False)
        user_special_liked = ArticleLike.objects.filter(user=user, special_like=True)

        if not is_owner:
            if not user_special_liked:
                special_like = request.data.get('special_like', False)
                if special_like:
                    ArticleLike.objects.create(
                        user=user,
                        article=article,
                        special_like=True
                    )

                    return Response(
                        {'details': 'Superliked article.'},
                        status=status.HTTP_201_CREATED
                    )

            else:
                return Response(
                    {'details': 'Can\'t special like twice.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not user_liked:
                ArticleLike.objects.create(
                    user=user,
                    article=article
                )

                return Response({'details': 'Liked article.'}, status=status.HTTP_201_CREATED)

            else:
                return Response(
                    {'details': 'Can\'t like twice.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'details': 'Can\'t like your own post.'},
            status=status.HTTP_403_FORBIDDEN
        )


class UnlikeArticleView(views.APIView):
    """ Handles unliking of articles. """
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    def delete(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_liked = ArticleLike.objects.filter(article=article,
                                                user=user,
                                                special_like=False)

        user_special_liked = ArticleLike.objects.filter(article=article,
                                                        user=user,
                                                        special_like=True)

        # TODO Not sure if the is_owner check is needed. But I'll save it just in case.
        # TODO Maybe I don't need to check for special/normal lieks here.
        if not is_owner:
            if user_special_liked:
                if request.data.get('special_like'):
                    user_special_liked.delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)

            if user_liked:
                user_liked.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            else:
                return Response(
                    {'details': 'Can\'t unlike without liking.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'details': 'Can\'t like your own post.'},
            status=status.HTTP_403_FORBIDDEN
        )


class VoteCommentView(views.APIView):
    """ Handles creation of comment votes. """
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        user = request.user
        comment = get_object_or_404(Comment, pk=pk)

        user_voted = CommentVote.objects.filter(user=user)

        if not comment.deleted:
            if not user_voted:
                if request.data.get('downvote'):
                    CommentVote.objects.create(
                        downvote=True,
                        user=user,
                        comment=comment
                    )

                else:
                    CommentVote.objects.create(
                        user=user,
                        comment=comment
                    )

                return Response(
                    {'details': 'Voted on comment.'},
                    status=status.HTTP_201_CREATED
                )

            else:
                return Response(
                    {'details': 'Can\'t vote twice.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'Can\'t vote on a deleted comment.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteCommentVoteView(views.APIView):
    """ Handles deletion of comment votes. """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        user = request.user

        comment = get_object_or_404(Comment, pk=pk)
        user_voted = CommentVote.objects.filter(comment=comment, user=user)

        if user_voted:
            user_voted.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(
                {'details': 'Can\'t unvote without voting.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ArticleFeedView(generics.ListAPIView):
    serializer_class = ArticleFeedSerializer
    pagination_class = FeedPagination

    def get_queryset(self):
        """
        Filters the queryset by:
            gets all the articles from followed users and followed article.\n
            Ordered by newest - oldest.
        """
        user = self.request.user

        qs = Article.objects.all().order_by('id')

        if user.is_authenticated:
            # Gets all articles with the tags that the user is following.
            tags = user.followed_tags.all()
            tags_articles = Article.objects.filter(tags__in=tags).distinct()

            # Gets all articles with the owners that the user is following.
            following = user.following.values_list('user_followed', flat=True)
            following_articles = Article.objects.filter(user_id__in=following).distinct()

            # Combines the two querysets
            qs = tags_articles | following_articles
            # Removes all the users own articles from
            # the queryset and orders it by newest to oldest.
            qs = qs.exclude(user=self.request.user).order_by('id')

            return qs

        return qs

    def list(self, request, *args, **kwargs):
        user = self.request.user

        queryset = self.filter_queryset(self.get_queryset())

        response_data = []

        if user.is_authenticated:
            followed_tags = FollowedTagsSerializer('', context={'request': self.request}).data
            followed_users = FollowedUsersSerializer('', context={'request': self.request}).data
            response_data.extend((followed_tags, followed_users,))

        page = self.paginate_queryset(queryset)
        if page is not None:
            articles = self.get_serializer(page, many=True).data
            response_data.append(articles)
            return self.get_paginated_response(response_data)

        articles = self.get_serializer(queryset, many=True).data
        response_data.append(articles)

        return Response(response_data)


class FollowTagView(views.APIView):
    """ Handles following of tags. """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        user = request.user
        tag_to_follow = get_object_or_404(Tag, slug=slug)

        already_following = tag_to_follow.followers.all().filter(pk=user.id)

        if not already_following:
            tag_to_follow.followers.add(user)

            return Response(
                {'details': 'Follow successful.'},
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {'details': 'Already following.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UnfollowTagView(views.APIView):
    """ Handles unfollowing of tags. """
    permission_classes = (IsAuthenticated,)

    def delete(self, request, slug):
        user = request.user
        tag_to_unfollow = get_object_or_404(Tag, slug=slug)

        following_obj = tag_to_unfollow.followers.filter(pk=user.id)

        if following_obj:
            tag_to_unfollow.followers.remove(user)

            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(
                {'details': 'You\'re not following that tag.'},
                status=status.HTTP_400_BAD_REQUEST
            )
