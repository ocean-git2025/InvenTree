"""Serializers for stock threshold plugin."""

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import StockItemThreshold


class StockItemThresholdSerializer(serializers.ModelSerializer):
    """Serializer for StockItemThreshold model."""
    
    class Meta:
        """Meta options for serializer."""
        model = StockItemThreshold
        fields = [
            'pk',
            'stock_item',
            'threshold',
            'enabled',
            'is_low_stock',
            'quantity_below_threshold',
            'created',
            'updated'
        ]
        read_only_fields = ['pk', 'created', 'updated', 'is_low_stock', 'quantity_below_threshold']
    
    is_low_stock = serializers.BooleanField(read_only=True)
    quantity_below_threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=5,
        read_only=True
    )


class StockItemThresholdBriefSerializer(serializers.Serializer):
    """Brief serializer for threshold info to be embedded in StockItem responses."""
    
    threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=5,
        required=False,
        allow_null=True
    )
    enabled = serializers.BooleanField(required=False, allow_null=True)
    is_low_stock = serializers.BooleanField(required=False, allow_null=True)
    quantity_below_threshold = serializers.DecimalField(
        max_digits=15,
        decimal_places=5,
        required=False,
        allow_null=True
    )
