from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.translation import gettext_lazy as _

from company.risk_models import (
    SupplierRisk, SupplyChainRisk, RiskMitigationStrategy,
    AlternativeSupplierSuggestion, RiskEvent, RiskLevel
)
from company.risk_serializers import (
    SupplierRiskSerializer, SupplyChainRiskSerializer,
    RiskMitigationStrategySerializer, AlternativeSupplierSuggestionSerializer,
    RiskEventSerializer, SupplierRiskSummarySerializer,
    SupplyChainRiskSummarySerializer
)


class IsStaffOrReadOnly(permissions.BasePermission):
    """Custom permission to allow staff users to edit, others read-only"""
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to staff users
        return request.user and request.user.is_staff


class SupplierRiskViewSet(viewsets.ModelViewSet):
    """API endpoint for managing SupplierRisk objects"""
    
    queryset = SupplierRisk.objects.all()
    serializer_class = SupplierRiskSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'supplier', 'overall_risk_level', 'is_alert_triggered',
        'last_assessment_date', 'next_assessment_date'
    ]
    
    search_fields = [
        'supplier__name', 'notes'
    ]
    
    ordering_fields = [
        'supplier__name', 'overall_risk_score', 'last_assessment_date',
        'financial_risk_score', 'delivery_risk_score',
        'quality_risk_score', 'geographical_risk_score'
    ]
    
    ordering = ['-overall_risk_score']
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate risk scores for a specific supplier"""
        risk = self.get_object()
        
        # Recalculate delivery risk
        risk.delivery_risk_score = risk.calculate_delivery_risk()
        risk.save()
        
        serializer = self.get_serializer(risk)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of supplier risks"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = SupplierRiskSummarySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get only high and critical risk suppliers"""
        queryset = self.get_queryset().filter(
            overall_risk_level__in=[RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SupplyChainRiskViewSet(viewsets.ModelViewSet):
    """API endpoint for managing SupplyChainRisk objects"""
    
    queryset = SupplyChainRisk.objects.all()
    serializer_class = SupplyChainRiskSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'part', 'risk_level', 'single_source_risk',
        'long_lead_time_risk', 'high_value_risk',
        'last_assessment_date'
    ]
    
    search_fields = [
        'part__name', 'part__description', 'notes'
    ]
    
    ordering_fields = [
        'part__name', 'risk_level', 'stockout_risk_score',
        'last_assessment_date'
    ]
    
    ordering = ['-stockout_risk_score']
    
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate risk scores for a specific part"""
        risk = self.get_object()
        risk.save()  # This triggers recalculation
        
        serializer = self.get_serializer(risk)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of supply chain risks"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = SupplyChainRiskSummarySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_risk(self, request):
        """Get only high and critical risk parts"""
        queryset = self.get_queryset().filter(
            risk_level__in=[RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def single_source(self, request):
        """Get parts that are single-sourced"""
        queryset = self.get_queryset().filter(single_source_risk=True)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RiskMitigationStrategyViewSet(viewsets.ModelViewSet):
    """API endpoint for managing RiskMitigationStrategy objects"""
    
    queryset = RiskMitigationStrategy.objects.all()
    serializer_class = RiskMitigationStrategySerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'part', 'strategy_type', 'implemented',
        'implementation_date'
    ]
    
    search_fields = [
        'part__name', 'strategy_type', 'description', 'notes'
    ]
    
    ordering_fields = [
        'part__name', 'strategy_type', 'implemented',
        'expected_effectiveness', 'implementation_date'
    ]
    
    ordering = ['-expected_effectiveness']
    
    @action(detail=False, methods=['get'])
    def implemented(self, request):
        """Get only implemented strategies"""
        queryset = self.get_queryset().filter(implemented=True)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def not_implemented(self, request):
        """Get only strategies that are not implemented"""
        queryset = self.get_queryset().filter(implemented=False)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AlternativeSupplierSuggestionViewSet(viewsets.ModelViewSet):
    """API endpoint for managing AlternativeSupplierSuggestion objects"""
    
    queryset = AlternativeSupplierSuggestion.objects.all()
    serializer_class = AlternativeSupplierSuggestionSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'part', 'suggested_supplier', 'reviewed',
        'review_date'
    ]
    
    search_fields = [
        'part__name', 'suggested_supplier__name', 'reason', 'review_notes'
    ]
    
    ordering_fields = [
        'part__name', 'suggested_supplier__name', 'similarity_score',
        'reviewed', 'review_date'
    ]
    
    ordering = ['-similarity_score']
    
    @action(detail=False, methods=['get'])
    def unreviewed(self, request):
        """Get only unreviewed suggestions"""
        queryset = self.get_queryset().filter(reviewed=False)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """Mark a suggestion as reviewed"""
        suggestion = self.get_object()
        suggestion.reviewed = True
        
        # Update review notes if provided
        review_notes = request.data.get('review_notes', None)
        if review_notes:
            suggestion.review_notes = review_notes
        
        suggestion.save()
        serializer = self.get_serializer(suggestion)
        return Response(serializer.data)


class RiskEventViewSet(viewsets.ModelViewSet):
    """API endpoint for managing RiskEvent objects"""
    
    queryset = RiskEvent.objects.all()
    serializer_class = RiskEventSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'category', 'severity', 'resolved',
        'event_date', 'resolution_date',
        'affected_suppliers', 'affected_parts'
    ]
    
    search_fields = [
        'title', 'description', 'resolution_notes'
    ]
    
    ordering_fields = [
        'event_date', 'severity', 'resolved',
        'title'
    ]
    
    ordering = ['-event_date']
    
    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get only unresolved risk events"""
        queryset = self.get_queryset().filter(resolved=False)
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_severity(self, request):
        """Get only high and critical severity events"""
        queryset = self.get_queryset().filter(
            severity__in=[RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an event as resolved"""
        event = self.get_object()
        event.resolved = True
        
        # Update resolution notes if provided
        resolution_notes = request.data.get('resolution_notes', None)
        if resolution_notes:
            event.resolution_notes = resolution_notes
        
        event.save()
        serializer = self.get_serializer(event)
        return Response(serializer.data)
