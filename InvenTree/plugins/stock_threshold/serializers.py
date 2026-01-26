"""Serializers for Stock Threshold plugin."""

from rest_framework import serializers

from .models import StockThreshold


class StockThresholdSerializer(serializers.ModelSerializer):
    """Serializer for StockThreshold model."""

    class Meta:
        """Meta options for StockThresholdSerializer."""
        model = StockThreshold
        fields = ['part', 'stock_threshold']
        read_only_fields = ['part']
