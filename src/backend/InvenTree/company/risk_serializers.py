from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from company.models import Company
from company.risk_models import (
    SupplierRisk, SupplyChainRisk, RiskMitigationStrategy,
    AlternativeSupplierSuggestion, RiskEvent, RiskLevel, RiskCategory
)
from part.models import Part


class RiskLevelField(serializers.ChoiceField):
    """Custom field for RiskLevel choices with labels"""
    def __init__(self, **kwargs):
        super().__init__(choices=RiskLevel.choices, **kwargs)
    
    def to_representation(self, value):
        """Return both value and label for display"""
        if value is None:
            return None
        return {
            'value': value,
            'label': RiskLevel(value).label
        }


class RiskCategoryField(serializers.ChoiceField):
    """Custom field for RiskCategory choices with labels"""
    def __init__(self, **kwargs):
        super().__init__(choices=RiskCategory.choices, **kwargs)
    
    def to_representation(self, value):
        """Return both value and label for display"""
        if value is None:
            return None
        return {
            'value': value,
            'label': RiskCategory(value).label
        }


class SupplierRiskSerializer(serializers.ModelSerializer):
    """Serializer for SupplierRisk model"""
    
    supplier = serializers.PrimaryKeyRelatedField(queryset=Company.objects.filter(is_supplier=True))
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    overall_risk_score = serializers.IntegerField(read_only=True)
    overall_risk_level = RiskLevelField(read_only=True)
    is_alert_triggered = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SupplierRisk
        fields = [
            'id', 'supplier', 'supplier_name',
            'financial_risk_score', 'delivery_risk_score',
            'quality_risk_score', 'geographical_risk_score',
            'overall_risk_score', 'overall_risk_level',
            'alert_threshold', 'is_alert_triggered',
            'last_assessment_date', 'next_assessment_date',
            'notes'
        ]
        read_only_fields = ['overall_risk_score', 'overall_risk_level', 'is_alert_triggered']
    
    def validate(self, data):
        """Custom validation for supplier risk data"""
        # Ensure risk scores are within valid range
        for field in ['financial_risk_score', 'delivery_risk_score', 'quality_risk_score', 'geographical_risk_score']:
            if field in data and (data[field] < 0 or data[field] > 100):
                raise serializers.ValidationError({
                    field: _('Risk score must be between 0 and 100')
                })
        
        return data


class SupplyChainRiskSerializer(serializers.ModelSerializer):
    """Serializer for SupplyChainRisk model"""
    
    part = serializers.PrimaryKeyRelatedField(queryset=Part.objects.all())
    part_name = serializers.CharField(source='part.full_name', read_only=True)
    risk_level = RiskLevelField()
    stockout_risk_score = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = SupplyChainRisk
        fields = [
            'id', 'part', 'part_name',
            'risk_level', 'single_source_risk',
            'long_lead_time_risk', 'high_value_risk',
            'stockout_risk_score', 'last_assessment_date',
            'notes'
        ]
        read_only_fields = ['stockout_risk_score', 'single_source_risk']


class RiskMitigationStrategySerializer(serializers.ModelSerializer):
    """Serializer for RiskMitigationStrategy model"""
    
    part = serializers.PrimaryKeyRelatedField(queryset=Part.objects.all())
    part_name = serializers.CharField(source='part.full_name', read_only=True)
    
    class Meta:
        model = RiskMitigationStrategy
        fields = [
            'id', 'part', 'part_name',
            'strategy_type', 'description',
            'implementation_cost', 'expected_effectiveness',
            'implemented', 'implementation_date',
            'notes'
        ]
    
    def validate_expected_effectiveness(self, value):
        """Validate expected effectiveness is within 0-100 range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(_('Expected effectiveness must be between 0 and 100'))
        return value


class AlternativeSupplierSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AlternativeSupplierSuggestion model"""
    
    part = serializers.PrimaryKeyRelatedField(queryset=Part.objects.all())
    part_name = serializers.CharField(source='part.full_name', read_only=True)
    suggested_supplier = serializers.PrimaryKeyRelatedField(queryset=Company.objects.filter(is_supplier=True))
    suggested_supplier_name = serializers.CharField(source='suggested_supplier.name', read_only=True)
    
    class Meta:
        model = AlternativeSupplierSuggestion
        fields = [
            'id', 'part', 'part_name',
            'suggested_supplier', 'suggested_supplier_name',
            'similarity_score', 'reason',
            'reviewed', 'review_date',
            'review_notes'
        ]
    
    def validate_similarity_score(self, value):
        """Validate similarity score is within 0-100 range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(_('Similarity score must be between 0 and 100'))
        return value


class RiskEventSerializer(serializers.ModelSerializer):
    """Serializer for RiskEvent model"""
    
    category = RiskCategoryField()
    severity = RiskLevelField()
    affected_suppliers = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.filter(is_supplier=True),
        many=True, required=False
    )
    affected_parts = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(),
        many=True, required=False
    )
    
    # Read-only fields for display
    affected_supplier_names = serializers.SerializerMethodField()
    affected_part_names = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskEvent
        fields = [
            'id', 'event_date', 'title', 'description',
            'category', 'severity',
            'affected_suppliers', 'affected_supplier_names',
            'affected_parts', 'affected_part_names',
            'resolved', 'resolution_date',
            'resolution_notes'
        ]
    
    def get_affected_supplier_names(self, obj):
        """Get list of affected supplier names"""
        return [supplier.name for supplier in obj.affected_suppliers.all()]
    
    def get_affected_part_names(self, obj):
        """Get list of affected part names"""
        return [part.full_name for part in obj.affected_parts.all()]


class SupplierRiskSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for supplier risk - used for quick overviews"""
    
    supplier_name = serializers.CharField(source='supplier.name')
    overall_risk_score = serializers.IntegerField()
    overall_risk_level = RiskLevelField()
    is_alert_triggered = serializers.BooleanField()
    
    class Meta:
        model = SupplierRisk
        fields = [
            'id', 'supplier', 'supplier_name',
            'overall_risk_score', 'overall_risk_level',
            'is_alert_triggered', 'last_assessment_date'
        ]
        read_only_fields = fields


class SupplyChainRiskSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for supply chain risk - used for quick overviews"""
    
    part_name = serializers.CharField(source='part.full_name')
    risk_level = RiskLevelField()
    stockout_risk_score = serializers.IntegerField()
    
    class Meta:
        model = SupplyChainRisk
        fields = [
            'id', 'part', 'part_name',
            'risk_level', 'stockout_risk_score',
            'single_source_risk', 'last_assessment_date'
        ]
        read_only_fields = fields
