from django.shortcuts import get_object_or_404
from django.http import Http404

from rest_framework import viewsets, views, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Article, ArticleLike, Comment, CommentVote
from .serializers import ArticleSerializer, CommentSerializer
from .permissions import IsOwnArticle


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnArticle,)
    lookup_field = 'slug'


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnArticle,)

    def destroy(self, request, *args, **kwargs):
        try:
            comment = self.get_object()
            comment.deleted = True
            comment.save()
        except Http404:
            return Response(data='could not delete', status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SaveArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    """ Handles saving of articles. """
    def post(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_has_saved = article.saves.filter(pk=user.id)

        if not is_owner:
            if not user_has_saved:
                user.saved_articles.add(article)

                return Response(
                    {'details': 'Saved article'},
                    status=status.HTTP_200_OK
                )

            else:
                return Response(
                    {'details': 'You have already saved this article'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'You can\'t save your own article'},
                status=status.HTTP_403_FORBIDDEN
            )


class UnsaveArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    """ Handles saving of articles. """
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
                    {'details': 'You must save before you can unsave'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {'details': 'You unsave your own post'},
                status=status.HTTP_403_FORBIDDEN
            )


class LikeArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    """ Handles creation of article likes. """
    def post(self, request, slug):
        user = request.user
        article = get_object_or_404(Article, slug=slug)

        is_owner = article.user.id == request.user.id

        user_liked = ArticleLike.objects.filter(user=user, special_like=False)
        user_special_liked = ArticleLike.objects.filter(user=user, special_like=True)

        if not is_owner:
            if not user_special_liked:
                if request.data.get('special_like'):
                    ArticleLike.objects.create(
                        user=user,
                        article=article,
                        special_like=True
                    )

                    return Response(
                        {'details': 'Superliked article'},
                        status=status.HTTP_201_CREATED
                    )

            else:
                return Response(
                    {'details': 'Can\'t special like twice'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not user_liked:
                ArticleLike.objects.create(
                    user=user,
                    article=article
                )

                return Response({'details': 'Liked article'}, status=status.HTTP_201_CREATED)

            else:
                return Response(
                    {'details': 'Can\'t like twice'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'details': 'Can\'t like your own post.'},
            status=status.HTTP_403_FORBIDDEN
        )


class UnlikeArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'slug'

    """ Handles deletion of article likes. """
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
                    {'details': 'Can\'t unlike without liking'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {'details': 'Can\'t like your own post.'},
            status=status.HTTP_403_FORBIDDEN
        )


class UpvoteCommentView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """ Handles creation of comment votes. """
    def post(self, request, pk):
        user = request.user
        comment = get_object_or_404(Comment, pk=pk)

        user_voted = CommentVote.objects.filter(user=user)

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
                {'details': 'Voted on comment'},
                status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {'details': 'Can\'t vote twice'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DeleteCommentVoteView(views.APIView):
    permission_classes = (IsAuthenticated,)

    """ Handles deletion of comment votes. """
    def delete(self, request, pk):
        user = request.user

        comment = get_object_or_404(Comment, pk=pk)
        user_voted = CommentVote.objects.filter(comment=comment, user=user)

        if user_voted:
            user_voted.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(
                {'details': 'Can\'t unvote without voting'},
                status=status.HTTP_400_BAD_REQUEST
            )
