"""JSON serializers for risk management models."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from InvenTree.serializers import InvenTreeModelSerializer
from .models import Company, SupplierPart
from .risk_models import (
    RiskLevel, RiskCategory, RiskThreshold, SupplierRiskAssessment,
    SupplyChainRiskAlert, RiskMitigationStrategy, AlternativeSupplierRecommendation
)


class RiskThresholdSerializer(InvenTreeModelSerializer):
    """Serializer for RiskThreshold model."""
    
    class Meta:
        """Metaclass options."""
        model = RiskThreshold
        fields = [
            'pk',
            'category',
            'low_threshold',
            'medium_threshold',
            'high_threshold',
            'active',
            'created',
            'updated',
        ]
        read_only_fields = ['created', 'updated']


class SupplierRiskAssessmentSerializer(InvenTreeModelSerializer):
    """Serializer for SupplierRiskAssessment model."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        """Metaclass options."""
        model = SupplierRiskAssessment
        fields = [
            'pk',
            'supplier',
            'supplier_name',
            'assessment_date',
            'financial_score',
            'delivery_score',
            'quality_score',
            'geographical_score',
            'overall_score',
            'overall_risk_level',
            'notes',
            'created',
            'updated',
        ]
        read_only_fields = ['overall_score', 'overall_risk_level', 'created', 'updated']


class SupplyChainRiskAlertSerializer(InvenTreeModelSerializer):
    """Serializer for SupplyChainRiskAlert model."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    resolved_by_username = serializers.CharField(source='resolved_by.username', read_only=True, allow_null=True)
    
    class Meta:
        """Metaclass options."""
        model = SupplyChainRiskAlert
        fields = [
            'pk',
            'supplier',
            'supplier_name',
            'alert_date',
            'risk_level',
            'alert_type',
            'message',
            'resolved',
            'resolved_date',
            'resolved_by',
            'resolved_by_username',
            'created',
            'updated',
        ]
        read_only_fields = ['resolved_date', 'created', 'updated']


class RiskMitigationStrategySerializer(InvenTreeModelSerializer):
    """Serializer for RiskMitigationStrategy model."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    
    class Meta:
        """Metaclass options."""
        model = RiskMitigationStrategy
        fields = [
            'pk',
            'supplier',
            'supplier_name',
            'strategy_name',
            'risk_category',
            'description',
            'implemented_date',
            'effective',
            'created',
            'updated',
        ]
        read_only_fields = ['created', 'updated']


class AlternativeSupplierRecommendationSerializer(InvenTreeModelSerializer):
    """Serializer for AlternativeSupplierRecommendation model."""
    
    primary_supplier_name = serializers.CharField(source='primary_supplier.name', read_only=True)
    alternative_supplier_name = serializers.CharField(source='alternative_supplier.name', read_only=True)
    part_sku = serializers.CharField(source='part.SKU', read_only=True)
    part_name = serializers.CharField(source='part.part.name', read_only=True)
    
    class Meta:
        """Metaclass options."""
        model = AlternativeSupplierRecommendation
        fields = [
            'pk',
            'primary_supplier',
            'primary_supplier_name',
            'alternative_supplier',
            'alternative_supplier_name',
            'part',
            'part_sku',
            'part_name',
            'recommendation_date',
            'reason',
            'priority',
            'created',
            'updated',
        ]
        read_only_fields = ['created', 'updated']
