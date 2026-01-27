"""API views for risk management models."""

from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from InvenTree.api import ListCreateAPI, RetrieveUpdateDestroyAPI
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.permissions import IsAuthenticatedOrReadScope
from .risk_models import (
    RiskThreshold, SupplierRiskAssessment, SupplyChainRiskAlert,
    RiskMitigationStrategy, AlternativeSupplierRecommendation
)
from .risk_serializers import (
    RiskThresholdSerializer, SupplierRiskAssessmentSerializer,
    SupplyChainRiskAlertSerializer, RiskMitigationStrategySerializer,
    AlternativeSupplierRecommendationSerializer
)


class RiskThresholdList(ListCreateAPI):
    """API endpoint for accessing a list of RiskThreshold objects."""
    
    serializer_class = RiskThresholdSerializer
    queryset = RiskThreshold.objects.all()
    permission_classes = [IsAuthenticatedOrReadScope]
    
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['category', 'active']
    search_fields = ['category']
    ordering_fields = ['category', 'active', 'created', 'updated']
    ordering = 'category'


class RiskThresholdDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail of a single RiskThreshold object."""
    
    queryset = RiskThreshold.objects.all()
    serializer_class = RiskThresholdSerializer
    permission_classes = [IsAuthenticatedOrReadScope]


class SupplierRiskAssessmentList(ListCreateAPI):
    """API endpoint for accessing a list of SupplierRiskAssessment objects."""
    
    serializer_class = SupplierRiskAssessmentSerializer
    queryset = SupplierRiskAssessment.objects.all().select_related('supplier')
    permission_classes = [IsAuthenticatedOrReadScope]
    
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['supplier', 'overall_risk_level', 'assessment_date']
    search_fields = ['supplier__name', 'notes']
    ordering_fields = ['assessment_date', 'overall_score', 'overall_risk_level', 'supplier__name']
    ordering = '-assessment_date'


class SupplierRiskAssessmentDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail of a single SupplierRiskAssessment object."""
    
    queryset = SupplierRiskAssessment.objects.all().select_related('supplier')
    serializer_class = SupplierRiskAssessmentSerializer
    permission_classes = [IsAuthenticatedOrReadScope]


class SupplyChainRiskAlertList(ListCreateAPI):
    """API endpoint for accessing a list of SupplyChainRiskAlert objects."""
    
    serializer_class = SupplyChainRiskAlertSerializer
    queryset = SupplyChainRiskAlert.objects.all().select_related('supplier', 'resolved_by')
    permission_classes = [IsAuthenticatedOrReadScope]
    
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['supplier', 'risk_level', 'alert_type', 'resolved', 'alert_date']
    search_fields = ['supplier__name', 'message']
    ordering_fields = ['alert_date', 'risk_level', 'supplier__name', 'resolved']
    ordering = '-alert_date'


class SupplyChainRiskAlertDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail of a single SupplyChainRiskAlert object."""
    
    queryset = SupplyChainRiskAlert.objects.all().select_related('supplier', 'resolved_by')
    serializer_class = SupplyChainRiskAlertSerializer
    permission_classes = [IsAuthenticatedOrReadScope]


class RiskMitigationStrategyList(ListCreateAPI):
    """API endpoint for accessing a list of RiskMitigationStrategy objects."""
    
    serializer_class = RiskMitigationStrategySerializer
    queryset = RiskMitigationStrategy.objects.all().select_related('supplier')
    permission_classes = [IsAuthenticatedOrReadScope]
    
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['supplier', 'risk_category', 'effective', 'implemented_date']
    search_fields = ['supplier__name', 'strategy_name', 'description']
    ordering_fields = ['strategy_name', 'supplier__name', 'risk_category', 'implemented_date']
    ordering = 'strategy_name'


class RiskMitigationStrategyDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail of a single RiskMitigationStrategy object."""
    
    queryset = RiskMitigationStrategy.objects.all().select_related('supplier')
    serializer_class = RiskMitigationStrategySerializer
    permission_classes = [IsAuthenticatedOrReadScope]


class AlternativeSupplierRecommendationList(ListCreateAPI):
    """API endpoint for accessing a list of AlternativeSupplierRecommendation objects."""
    
    serializer_class = AlternativeSupplierRecommendationSerializer
    queryset = AlternativeSupplierRecommendation.objects.all().select_related(
        'primary_supplier', 'alternative_supplier', 'part'
    )
    permission_classes = [IsAuthenticatedOrReadScope]
    
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['primary_supplier', 'alternative_supplier', 'part', 'priority']
    search_fields = ['primary_supplier__name', 'alternative_supplier__name', 'part__SKU', 'reason']
    ordering_fields = ['priority', 'recommendation_date', 'primary_supplier__name', 'alternative_supplier__name']
    ordering = 'priority'


class AlternativeSupplierRecommendationDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail of a single AlternativeSupplierRecommendation object."""
    
    queryset = AlternativeSupplierRecommendation.objects.all().select_related(
        'primary_supplier', 'alternative_supplier', 'part'
    )
    serializer_class = AlternativeSupplierRecommendationSerializer
    permission_classes = [IsAuthenticatedOrReadScope]
