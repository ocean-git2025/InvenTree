"""Stock Threshold plugin models."""

from django.db import models
from part.models import Part


class StockThreshold(models.Model):
    """Model to store stock thresholds for parts."""

    # One-to-one relationship with Part
    part = models.OneToOneField(
        Part,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='stock_threshold'
    )

    # Stock threshold value
    stock_threshold = models.IntegerField(
        default=0,
        help_text="Minimum stock level before notification"
    )

    class Meta:
        """Meta options for StockThreshold model."""
        verbose_name = "Stock Threshold"
        verbose_name_plural = "Stock Thresholds"

    def __str__(self):
        """String representation of StockThreshold."""
        return f"{self.part} - Threshold: {self.stock_threshold}"
