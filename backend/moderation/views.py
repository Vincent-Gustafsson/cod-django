from django.http.response import Http404
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer
from .permissions import IsModeratorOrCreateOnly


class ReportViewSet(viewsets.GenericViewSet,
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

        if report_obj_type:
            if report_obj_type == 'articles':
                qs = qs.filter(article__isnull=False)

            elif report_obj_type == 'comments':
                qs = qs.filter(comment__isnull=False)

            elif report_obj_type == 'users':
                qs = qs.filter(user__isnull=False)

        if moderated:
            qs = qs.filter(moderated=True)
        else:
            qs = qs.filter(moderated=False)

        return qs

    def destroy(self, request, *args, **kwargs):
        try:
            report = self.get_object()
            report.moderated = True
            report.save()
        except Http404:
            return Response(data='could not mark moderated', status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
