from django.shortcuts import get_object_or_404

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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnArticle,)


class LikeArticleView(views.APIView):
    permission_classes = (IsAuthenticated,)
    """ Handles creation of article likes. """
    def post(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

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
    """ Handles deletion of article likes. """
    def delete(self, request, pk):
        user = request.user
        article = get_object_or_404(Article, pk=pk)

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
