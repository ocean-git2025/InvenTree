import logging
from django.utils.timezone import now, timedelta
from django.db.models import Avg, Count, F
from .models import Company, SupplierPart, PurchaseOrder, PurchaseOrderLineItem
from .risk_models import (
    RiskLevel, RiskCategory, RiskThreshold, SupplierRiskAssessment,
    SupplyChainRiskAlert, RiskMitigationStrategy, AlternativeSupplierRecommendation
)

logger = logging.getLogger(__name__)


def calculate_supplier_risk(supplier_id):
    """Calculate risk assessment for a specific supplier.
    
    Args:
        supplier_id (int): ID of the supplier to assess
    
    Returns:
        SupplierRiskAssessment: The created or updated risk assessment
    """
    try:
        supplier = Company.objects.get(pk=supplier_id, is_supplier=True)
    except Company.DoesNotExist:
        logger.error(f"Supplier with ID {supplier_id} not found or is not a supplier")
        return None
    
    # Calculate financial risk (0-100)
    financial_score = calculate_financial_risk(supplier)
    
    # Calculate delivery risk (0-100)
    delivery_score = calculate_delivery_risk(supplier)
    
    # Calculate quality risk (0-100)
    quality_score = calculate_quality_risk(supplier)
    
    # Calculate geographical risk (0-100)
    geographical_score = calculate_geographical_risk(supplier)
    
    # Calculate overall risk score (weighted average)
    # Weights: financial=30%, delivery=30%, quality=30%, geographical=10%
    overall_score = (financial_score * 0.3) + (delivery_score * 0.3) + (quality_score * 0.3) + (geographical_score * 0.1)
    overall_score = round(overall_score, 2)
    
    # Determine overall risk level
    if overall_score < 30:
        overall_risk_level = RiskLevel.LOW
    elif overall_score < 70:
        overall_risk_level = RiskLevel.MEDIUM
    else:
        overall_risk_level = RiskLevel.HIGH
    
    # Create or update risk assessment
    assessment, created = SupplierRiskAssessment.objects.update_or_create(
        supplier=supplier,
        defaults={
            'financial_score': financial_score,
            'delivery_score': delivery_score,
            'quality_score': quality_score,
            'geographical_score': geographical_score,
            'overall_score': overall_score,
            'overall_risk_level': overall_risk_level,
            'assessment_date': now()
        }
    )
    
    # Check if we need to create a risk alert
    check_supply_chain_alert(supplier, overall_risk_level, overall_score)
    
    # Generate alternative supplier recommendations if needed
    if overall_risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
        generate_alternative_suppliers(supplier)
    
    logger.info(f"Risk assessment completed for supplier {supplier.name}: {overall_risk_level} ({overall_score})")
    return assessment


def calculate_financial_risk(supplier):
    """Calculate financial risk score for a supplier (0-100).
    
    Args:
        supplier (Company): Supplier instance
    
    Returns:
        float: Financial risk score (0-100)
    """
    # Default financial score (assuming no data)
    score = 50
    
    # In a real implementation, this would integrate with financial data sources
    # For now, we'll use dummy logic based on available data
    
    # Check if supplier has any financial indicators
    # For example, if supplier has a lot of open purchase orders with high values
    open_orders = PurchaseOrder.objects.filter(
        supplier=supplier,
        status__in=['PO_OPEN', 'PO_IN_PROGRESS']
    )
    
    if open_orders.exists():
        total_open_value = sum(order.total_price() for order in open_orders)
        # Higher open value might indicate higher financial risk
        if total_open_value > 100000:
            score += 20
        elif total_open_value > 50000:
            score += 10
    
    # Cap score at 100
    return min(score, 100)


def calculate_delivery_risk(supplier):
    """Calculate delivery risk score for a supplier (0-100).
    
    Args:
        supplier (Company): Supplier instance
    
    Returns:
        float: Delivery risk score (0-100)
    """
    # Calculate delivery performance based on past orders
    completed_orders = PurchaseOrder.objects.filter(
        supplier=supplier,
        status='PO_COMPLETED'
    ).prefetch_related('lines')
    
    if not completed_orders.exists():
        return 50  # No data, default to medium risk
    
    late_deliveries = 0
    total_deliveries = 0
    
    for order in completed_orders:
        for line in order.lines.all():
            if line.received_date and line.expected_delivery:
                total_deliveries += 1
                if line.received_date > line.expected_delivery:
                    late_deliveries += 1
    
    if total_deliveries == 0:
        return 50
    
    # Calculate late delivery percentage
    late_percentage = (late_deliveries / total_deliveries) * 100
    
    # Convert late percentage to risk score (higher late percentage = higher risk)
    score = late_percentage
    
    # Cap score at 100
    return min(score, 100)


def calculate_quality_risk(supplier):
    """Calculate quality risk score for a supplier (0-100).
    
    Args:
        supplier (Company): Supplier instance
    
    Returns:
        float: Quality risk score (0-100)
    """
    # Calculate quality performance based on received goods
    # In a real implementation, this would use inspection data
    # For now, we'll use dummy logic
    
    # Get all supplier parts
    supplier_parts = SupplierPart.objects.filter(supplier=supplier)
    
    if not supplier_parts.exists():
        return 50  # No data, default to medium risk
    
    # Dummy quality score based on number of supplier parts
    # In real implementation, this would use actual quality metrics
    score = 50
    
    # For example, if supplier has many parts, maybe higher quality risk
    if supplier_parts.count() > 100:
        score += 20
    elif supplier_parts.count() > 50:
        score += 10
    
    # Cap score at 100
    return min(score, 100)


def calculate_geographical_risk(supplier):
    """Calculate geographical risk score for a supplier (0-100).
    
    Args:
        supplier (Company): Supplier instance
    
    Returns:
        float: Geographical risk score (0-100)
    """
    # Calculate geographical risk based on supplier location
    # In a real implementation, this would use country risk data
    # For now, we'll use dummy logic
    
    score = 0
    
    # Get supplier address
    addresses = supplier.addresses.all()
    if addresses.exists():
        country = addresses.first().country
        # Example: higher risk for countries with political instability
        high_risk_countries = ['IR', 'SY', 'AF', 'YE', 'SD']
        medium_risk_countries = ['RU', 'CN', 'IN', 'BR', 'MX']
        
        if country in high_risk_countries:
            score = 80
        elif country in medium_risk_countries:
            score = 40
        else:
            score = 10
    
    return score


def check_supply_chain_alert(supplier, risk_level, risk_score):
    """Check if a supply chain risk alert should be created or updated.
    
    Args:
        supplier (Company): Supplier instance
        risk_level (RiskLevel): Current risk level
        risk_score (float): Current risk score
    """
    # Check if there's an existing open alert
    existing_alert = SupplyChainRiskAlert.objects.filter(
        supplier=supplier,
        resolved=False
    ).first()
    
    # Determine if we need to create/update an alert
    if risk_level == RiskLevel.HIGH:
        alert_type = 'high_risk'
        message = f"High risk detected for supplier {supplier.name} (score: {risk_score:.2f})"
        
        if existing_alert:
            # Update existing alert
            existing_alert.risk_level = risk_level
            existing_alert.message = message
            existing_alert.alert_date = now()
            existing_alert.save()
        else:
            # Create new alert
            SupplyChainRiskAlert.objects.create(
                supplier=supplier,
                risk_level=risk_level,
                alert_type=alert_type,
                message=message
            )
    elif risk_level == RiskLevel.MEDIUM:
        alert_type = 'medium_risk'
        message = f"Medium risk detected for supplier {supplier.name} (score: {risk_score:.2f})"
        
        if existing_alert and existing_alert.risk_level != RiskLevel.MEDIUM:
            # Update existing alert
            existing_alert.risk_level = risk_level
            existing_alert.message = message
            existing_alert.alert_date = now()
            existing_alert.save()
        elif not existing_alert:
            # Create new alert
            SupplyChainRiskAlert.objects.create(
                supplier=supplier,
                risk_level=risk_level,
                alert_type=alert_type,
                message=message
            )
    else:
        # Low risk, resolve any existing alerts
        if existing_alert:
            existing_alert.resolved = True
            existing_alert.resolved_date = now()
            existing_alert.save()


def generate_alternative_suppliers(supplier):
    """Generate alternative supplier recommendations for high/medium risk suppliers.
    
    Args:
        supplier (Company): Supplier instance
    """
    # Get all parts supplied by this supplier
    supplier_parts = SupplierPart.objects.filter(supplier=supplier)
    
    for supplier_part in supplier_parts:
        # Find other suppliers for the same part
        alternative_parts = SupplierPart.objects.filter(
            part=supplier_part.part,
            supplier__is_supplier=True,
            supplier__pk__ != supplier.pk
        ).exclude(supplier=supplier)
        
        for alternative_part in alternative_parts:
            # Check if recommendation already exists
            existing_recommendation = AlternativeSupplierRecommendation.objects.filter(
                primary_supplier=supplier,
                alternative_supplier=alternative_part.supplier,
                part=supplier_part
            ).first()
            
            if not existing_recommendation:
                # Create new recommendation
                AlternativeSupplierRecommendation.objects.create(
                    primary_supplier=supplier,
                    alternative_supplier=alternative_part.supplier,
                    part=supplier_part,
                    reason=f"Alternative supplier for part {supplier_part.part.name} (SKU: {supplier_part.SKU})",
                    priority='high' if supplier_part.is_primary else 'medium'
                )
    