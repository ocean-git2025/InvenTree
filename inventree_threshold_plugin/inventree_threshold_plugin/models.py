"""Models for the stock threshold plugin."""

from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

import stock.models


class StockItemThreshold(models.Model):
    """Model to store custom stock threshold for a StockItem.
    
    This model extends StockItem with a custom threshold value.
    When stock quantity falls below this threshold, it will be marked as low stock.
    """
    
    class Meta:
        """Meta options for the model."""
        verbose_name = _('Stock Item Threshold')
        verbose_name_plural = _('Stock Item Thresholds')
        
    stock_item = models.OneToOneField(
        stock.models.StockItem,
        on_delete=models.CASCADE,
        related_name='threshold_config',
        verbose_name=_('Stock Item'),
        help_text=_('The stock item this threshold applies to')
    )
    
    threshold = models.DecimalField(
        max_digits=15,
        decimal_places=5,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Threshold'),
        help_text=_('Minimum stock quantity before low stock warning is triggered')
    )
    
    enabled = models.BooleanField(
        default=True,
        verbose_name=_('Enabled'),
        help_text=_('Enable threshold checking for this stock item')
    )
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        """String representation."""
        return f"{self.stock_item.part.name} - Threshold: {self.threshold}"
    
    @property
    def is_low_stock(self) -> bool:
        """Check if the stock item is below threshold.
        
        Returns:
            True if stock quantity is below threshold and threshold is enabled
        """
        if not self.enabled:
            return False
        return self.stock_item.quantity < self.threshold
    
    @property
    def quantity_below_threshold(self):
        """Calculate how much stock is below threshold.
        
        Returns:
            The difference between threshold and current quantity (0 if above threshold)
        """
        if self.stock_item.quantity >= self.threshold:
            return 0
        return self.threshold - self.stock_item.quantity
