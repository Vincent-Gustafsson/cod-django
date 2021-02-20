from django.http.response import Http404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer
from .permissions import IsModeratorOrCreateOnly

# When I want to fetch all reports I'm actually going to have to send three requests.
# This is not very performant but I've already implemented the whole moderation system.

# If I want to change it to some kind of nested serializer with all the different objects
# in separate arrays I would've had to rewrite most of the code.

# But since the moderation dashboard won't be accessed as often as the rest of the website
# it's not as bad. There will be A LOT less requests from the moderation dashboard than
# the rest of the website. Thanks for coming to my TED Talk.
class ReportViewSet(viewsets.GenericViewSet,  # noqa
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin):
    serializer_class = ReportSerializer
    permission_classes = (IsModeratorOrCreateOnly,)

    def get_queryset(self):
        qs = Report.objects.all()

        report_obj_type = self.request.query_params.get('type', None)
        moderated = self.request.query_params.get('moderated', None)
        order = self.request.query_params.get('order_by', None)

        # Sorts by reported object type (article, comment or user).
        if report_obj_type:
            if report_obj_type == 'articles':
                qs = qs.filter(article__isnull=False)

            elif report_obj_type == 'comments':
                qs = qs.filter(comment__isnull=False)

            elif report_obj_type == 'users':
                qs = qs.filter(user__isnull=False)

        # Sorts by moderated (has the report been moderated yes/no).
        if moderated:
            qs = qs.filter(moderated=True)
        else:
            qs = qs.filter(moderated=False)

        # Sorts by newest or oldest.
        if order:
            if order == 'newest':
                qs = qs.order_by('-created_at')

            elif order == 'oldest':
                qs = qs.order_by('created_at')

        return qs

    def destroy(self, request, *args, **kwargs):
        try:
            report = self.get_object()
            report.moderated = True
            report.save()
        except Http404:
            return Response({'details': 'Couldn\'t mark moderated.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
