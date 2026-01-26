"""API views for Stock Threshold plugin."""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import StockThreshold
from .serializers import StockThresholdSerializer


class StockThresholdList(generics.ListCreateAPIView):
    """List all stock thresholds or create a new one."""

    permission_classes = [IsAuthenticated]
    queryset = StockThreshold.objects.all()
    serializer_class = StockThresholdSerializer


class StockThresholdDetail(generics.RetrieveUpdateAPIView):
    """Retrieve, update a stock threshold."""

    permission_classes = [IsAuthenticated]
    queryset = StockThreshold.objects.all()
    serializer_class = StockThresholdSerializer
    lookup_field = 'part'

    def get_object(self):
        """Get or create a StockThreshold object for the given part."""
        try:
            return super().get_object()
        except StockThreshold.DoesNotExist:
            # If no threshold exists for this part, create one with default value
            from part.models import Part
            part = Part.objects.get(pk=self.kwargs['part'])
            threshold = StockThreshold.objects.create(
                part=part,
                stock_threshold=0
            )
            return threshold
