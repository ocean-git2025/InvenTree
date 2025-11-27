from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q, F, Avg, Count, Sum
from datetime import timedelta

import InvenTree.helpers
from InvenTree.models import InvenTreeModel
from part.models import Part


class RiskLevel(models.TextChoices):
    """Risk level choices for suppliers and components"""
    LOW = 'low', _('Low Risk')
    MEDIUM = 'medium', _('Medium Risk')
    HIGH = 'high', _('High Risk')
    CRITICAL = 'critical', _('Critical Risk')


class RiskCategory(models.TextChoices):
    """Risk category choices"""
    FINANCIAL = 'financial', _('Financial Risk')
    DELIVERY = 'delivery', _('Delivery Risk')
    QUALITY = 'quality', _('Quality Risk')
    GEOGRAPHICAL = 'geographical', _('Geographical Risk')
    POLITICAL = 'political', _('Political Risk')
    ENVIRONMENTAL = 'environmental', _('Environmental Risk')


class SupplierRisk(InvenTreeModel):
    """Model to track supplier risk assessment"""
    
    supplier = models.OneToOneField(
        'Company',
        on_delete=models.CASCADE,
        related_name='risk_assessment',
        limit_choices_to={'is_supplier': True},
        verbose_name=_('Supplier')
    )
    
    # Risk scores (0-100, higher = higher risk)
    financial_risk_score = models.IntegerField(
        default=0,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Financial Risk Score'),
        help_text=_('Financial stability risk (0-100)')
    )
    
    delivery_risk_score = models.IntegerField(
        default=0,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Delivery Risk Score'),
        help_text=_('Delivery reliability risk (0-100)')
    )
    
    quality_risk_score = models.IntegerField(
        default=0,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Quality Risk Score'),
        help_text=_('Product quality risk (0-100)')
    )
    
    geographical_risk_score = models.IntegerField(
        default=0,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Geographical Risk Score'),
        help_text=_('Geographical/political risk (0-100)')
    )
    
    # Risk thresholds (for automatic alerts)
    alert_threshold = models.IntegerField(
        default=70,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Alert Threshold'),
        help_text=_('Risk score threshold for automatic alerts')
    )
    
    # Last assessment date
    last_assessment_date = models.DateField(
        auto_now=True,
        verbose_name=_('Last Assessment Date')
    )
    
    # Next scheduled assessment
    next_assessment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Next Assessment Date')
    )
    
    # Risk assessment notes
    notes = models.TextField(
        blank=True,
        verbose_name=_('Risk Assessment Notes')
    )
    
    class Meta:
        verbose_name = _('Supplier Risk Assessment')
        verbose_name_plural = _('Supplier Risk Assessments')
    
    def __str__(self):
        return f"{self.supplier.name} - Risk Assessment"
    
    @property
    def overall_risk_score(self):
        """Calculate overall risk score as average of all category scores"""
        scores = [
            self.financial_risk_score,
            self.delivery_risk_score,
            self.quality_risk_score,
            self.geographical_risk_score
        ]
        return sum(scores) // len(scores)
    
    @property
    def overall_risk_level(self):
        """Determine overall risk level based on score"""
        score = self.overall_risk_score
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    @property
    def is_alert_triggered(self):
        """Check if risk score exceeds alert threshold"""
        return self.overall_risk_score >= self.alert_threshold
    
    def calculate_delivery_risk(self):
        """Calculate delivery risk based on historical performance"""
        from order.models import PurchaseOrderLineItem
        
        # Get all purchase order line items for this supplier in the last 12 months
        cutoff_date = InvenTree.helpers.current_date() - timedelta(days=365)
        
        line_items = PurchaseOrderLineItem.objects.filter(
            order__supplier=self.supplier,
            order__order_date__gte=cutoff_date
        )
        
        if not line_items.exists():
            return 0  # No historical data, assume low risk
        
        # Calculate delivery metrics
        total_lines = line_items.count()
        
        # Overdue items
        overdue_items = line_items.filter(
            PurchaseOrderLineItem.OVERDUE_FILTER
        ).count()
        
        # Partially delivered items
        partial_items = line_items.filter(
            received__lt=F('quantity')
        ).count()
        
        # Calculate delivery risk score (0-100)
        overdue_ratio = overdue_items / total_lines if total_lines > 0 else 0
        partial_ratio = partial_items / total_lines if total_lines > 0 else 0
        
        # Weighted average: 60% overdue, 40% partial
        delivery_risk = (overdue_ratio * 60 + partial_ratio * 40) * 100
        
        return min(100, max(0, round(delivery_risk)))
    
    def save(self, *args, **kwargs):
        # Recalculate delivery risk before saving
        self.delivery_risk_score = self.calculate_delivery_risk()
        
        # Auto-set next assessment date if not provided
        if not self.next_assessment_date:
            self.next_assessment_date = InvenTree.helpers.current_date() + timedelta(days=90)
        
        super().save(*args, **kwargs)


class SupplyChainRisk(InvenTreeModel):
    """Model to track supply chain risk for parts/components"""
    
    part = models.OneToOneField(
        Part,
        on_delete=models.CASCADE,
        related_name='supply_chain_risk',
        verbose_name=_('Part')
    )
    
    # Risk assessment
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        verbose_name=_('Risk Level')
    )
    
    # Risk factors
    single_source_risk = models.BooleanField(
        default=False,
        verbose_name=_('Single Source Risk'),
        help_text=_('Part is only available from one supplier')
    )
    
    long_lead_time_risk = models.BooleanField(
        default=False,
        verbose_name=_('Long Lead Time Risk'),
        help_text=_('Part has excessively long lead time')
    )
    
    high_value_risk = models.BooleanField(
        default=False,
        verbose_name=_('High Value Risk'),
        help_text=_('Part has high monetary value')
    )
    
    # Stockout risk indicators
    stockout_risk_score = models.IntegerField(
        default=0,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Stockout Risk Score'),
        help_text=_('Likelihood of stockout (0-100)')
    )
    
    # Last assessment date
    last_assessment_date = models.DateField(
        auto_now=True,
        verbose_name=_('Last Assessment Date')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Risk Assessment Notes')
    )
    
    class Meta:
        verbose_name = _('Supply Chain Risk')
        verbose_name_plural = _('Supply Chain Risk Assessments')
    
    def __str__(self):
        return f"{self.part.full_name} - Supply Chain Risk"
    
    def calculate_stockout_risk(self):
        """Calculate stockout risk based on inventory and demand"""
        from stock.models import StockItem
        
        # Get current stock level
        current_stock = StockItem.objects.filter(
            part=self.part,
            StockItem.IN_STOCK_FILTER
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if current_stock == 0:
            return 100  # Out of stock, critical risk
        
        # Calculate inventory turnover (simplified)
        # In a real implementation, this would use historical demand data
        turnover_rate = self.estimate_turnover_rate()
        
        # Calculate days of inventory on hand
        if turnover_rate > 0:
            days_on_hand = 365 / turnover_rate
        else:
            days_on_hand = 999  # Very slow moving
        
        # Calculate stockout risk based on days on hand
        if days_on_hand < 7:
            return 90  # Critical risk
        elif days_on_hand < 30:
            return 70  # High risk
        elif days_on_hand < 90:
            return 40  # Medium risk
        else:
            return 10  # Low risk
    
    def estimate_turnover_rate(self):
        """Estimate inventory turnover rate"""
        from order.models import PurchaseOrderLineItem
        
        # Get total purchases in last 12 months
        cutoff_date = InvenTree.helpers.current_date() - timedelta(days=365)
        
        total_purchased = PurchaseOrderLineItem.objects.filter(
            part__part=self.part,
            order__order_date__gte=cutoff_date
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Get average stock level (simplified)
        from stock.models import StockItem
        avg_stock = StockItem.objects.filter(
            part=self.part,
            StockItem.IN_STOCK_FILTER
        ).aggregate(avg=Avg('quantity'))['avg'] or 0
        
        if avg_stock == 0:
            return 0
        
        return total_purchased / avg_stock
    
    def save(self, *args, **kwargs):
        # Check if part is single-sourced
        from .models import SupplierPart
        supplier_count = SupplierPart.objects.filter(part=self.part).count()
        self.single_source_risk = supplier_count <= 1
        
        # Calculate stockout risk
        self.stockout_risk_score = self.calculate_stockout_risk()
        
        # Determine overall risk level
        risk_factors = 0
        if self.single_source_risk:
            risk_factors += 30
        if self.long_lead_time_risk:
            risk_factors += 25
        if self.high_value_risk:
            risk_factors += 20
        
        # Combine with stockout risk
        combined_risk = (risk_factors + self.stockout_risk_score) // 2
        
        if combined_risk >= 80:
            self.risk_level = RiskLevel.CRITICAL
        elif combined_risk >= 60:
            self.risk_level = RiskLevel.HIGH
        elif combined_risk >= 40:
            self.risk_level = RiskLevel.MEDIUM
        else:
            self.risk_level = RiskLevel.LOW
        
        super().save(*args, **kwargs)


class RiskMitigationStrategy(InvenTreeModel):
    """Model to track risk mitigation strategies"""
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='mitigation_strategies',
        verbose_name=_('Part')
    )
    
    strategy_type = models.CharField(
        max_length=100,
        verbose_name=_('Strategy Type'),
        help_text=_('Type of mitigation strategy (e.g., Alternative Supplier, Safety Stock)')
    )
    
    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('Detailed description of the mitigation strategy')
    )
    
    implementation_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Implementation Cost'),
        help_text=_('Estimated cost to implement this strategy')
    )
    
    expected_effectiveness = models.IntegerField(
        default=50,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Expected Effectiveness'),
        help_text=_('Expected risk reduction effectiveness (0-100)')
    )
    
    implemented = models.BooleanField(
        default=False,
        verbose_name=_('Implemented'),
        help_text=_('Has this strategy been implemented?')
    )
    
    implementation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Implementation Date')
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_('Notes')
    )
    
    class Meta:
        verbose_name = _('Risk Mitigation Strategy')
        verbose_name_plural = _('Risk Mitigation Strategies')
    
    def __str__(self):
        return f"{self.part.full_name} - {self.strategy_type}"


class AlternativeSupplierSuggestion(InvenTreeModel):
    """Model to suggest alternative suppliers for high-risk parts"""
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='alternative_suppliers',
        verbose_name=_('Part')
    )
    
    suggested_supplier = models.ForeignKey(
        'Company',
        on_delete=models.CASCADE,
        related_name='suggested_for_parts',
        limit_choices_to={'is_supplier': True},
        verbose_name=_('Suggested Supplier')
    )
    
    similarity_score = models.IntegerField(
        default=50,
        validators=[models.MinValueValidator(0), models.MaxValueValidator(100)],
        verbose_name=_('Similarity Score'),
        help_text=_('How well this supplier matches the original (0-100)')
    )
    
    reason = models.TextField(
        blank=True,
        verbose_name=_('Reason'),
        help_text=_('Reason for suggesting this alternative supplier')
    )
    
    reviewed = models.BooleanField(
        default=False,
        verbose_name=_('Reviewed'),
        help_text=_('Has this suggestion been reviewed?')
    )
    
    review_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Review Date')
    )
    
    review_notes = models.TextField(
        blank=True,
        verbose_name=_('Review Notes')
    )
    
    class Meta:
        verbose_name = _('Alternative Supplier Suggestion')
        verbose_name_plural = _('Alternative Supplier Suggestions')
        unique_together = ('part', 'suggested_supplier')
    
    def __str__(self):
        return f"{self.part.full_name} - Alternative: {self.suggested_supplier.name}"


class RiskEvent(InvenTreeModel):
    """Model to track supply chain risk events"""
    
    event_date = models.DateField(
        default=InvenTree.helpers.current_date,
        verbose_name=_('Event Date')
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Event Title')
    )
    
    description = models.TextField(
        verbose_name=_('Event Description')
    )
    
    category = models.CharField(
        max_length=50,
        choices=RiskCategory.choices,
        verbose_name=_('Risk Category')
    )
    
    severity = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MEDIUM,
        verbose_name=_('Severity')
    )
    
    affected_suppliers = models.ManyToManyField(
        'Company',
        related_name='risk_events',
        blank=True,
        limit_choices_to={'is_supplier': True},
        verbose_name=_('Affected Suppliers')
    )
    
    affected_parts = models.ManyToManyField(
        Part,
        related_name='risk_events',
        blank=True,
        verbose_name=_('Affected Parts')
    )
    
    resolved = models.BooleanField(
        default=False,
        verbose_name=_('Resolved')
    )
    
    resolution_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Resolution Date')
    )
    
    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_('Resolution Notes')
    )
    
    class Meta:
        verbose_name = _('Risk Event')
        verbose_name_plural = _('Risk Events')
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.event_date} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.resolved and not self.resolution_date:
            self.resolution_date = InvenTree.helpers.current_date()
        super().save(*args, **kwargs)
