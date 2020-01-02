from .models import BlockRow
from rest_framework import viewsets
from .serializers import BlockSerializer


class BlockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = BlockRow.objects.all().order_by('pk_id')
    serializer_class = BlockSerializer