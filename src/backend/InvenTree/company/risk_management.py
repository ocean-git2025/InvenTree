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
    