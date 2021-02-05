from rest_framework import viewsets

from .models import Report
from .serializers import ReportSerializer


class ArticleReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user__isnull=False)
