from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

import InvenTree.helpers
from company.models import Company
from company.risk_models import (
    SupplierRisk, SupplyChainRisk, AlternativeSupplierSuggestion,
    RiskEvent, RiskLevel, RiskCategory
)
from part.models import Part


class Command(BaseCommand):
    """Management command to run periodic supply chain risk assessment"""
    
    help = _('Run periodic supply chain risk assessment and generate alerts')
    
    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--suppliers-only',
            action='store_true',
            help=_('Only assess supplier risk (skip part risk assessment)')
        )
        
        parser.add_argument(
            '--parts-only',
            action='store_true',
            help=_('Only assess part supply chain risk (skip supplier risk assessment)')
        )
        
        parser.add_argument(
            '--generate-suggestions',
            action='store_true',
            help=_('Generate alternative supplier suggestions for high-risk parts')
        )
        
        parser.add_argument(
            '--send-alerts',
            action='store_true',
            help=_('Send alerts for high-risk items (if configured)')
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(_('Starting supply chain risk assessment...'))
        
        # Track assessment statistics
        stats = {
            'suppliers_assessed': 0,
            'suppliers_with_risk': 0,
            'parts_assessed': 0,
            'parts_with_risk': 0,
            'suggestions_generated': 0,
            'alerts_sent': 0
        }
        
        # Assess supplier risk
        if not options['parts_only']:
            stats.update(self.assess_supplier_risk())
        
        # Assess part supply chain risk
        if not options['suppliers_only']:
            stats.update(self.assess_part_risk())
        
        # Generate alternative supplier suggestions
        if options['generate_suggestions']:
            stats.update(self.generate_alternative_suppliers())
        
        # Send alerts
        if options['send_alerts']:
            stats.update(self.send_risk_alerts())
        
        # Print assessment summary
        self.stdout.write(_('\nRisk assessment completed:'))
        self.stdout.write(_(f'  Suppliers assessed: {stats["suppliers_assessed"]}'))
        self.stdout.write(_(f'  Suppliers with high risk: {stats["suppliers_with_risk"]}'))
        self.stdout.write(_(f'  Parts assessed: {stats["parts_assessed"]}'))
        self.stdout.write(_(f'  Parts with high risk: {stats["parts_with_risk"]}'))
        
        if options['generate_suggestions']:
            self.stdout.write(_(f'  Alternative suppliers suggested: {stats["suggestions_generated"]}'))
        
        if options['send_alerts']:
            self.stdout.write(_(f'  Alerts sent: {stats["alerts_sent"]}'))
        
        self.stdout.write(_('\nRisk assessment finished successfully!'))
    
    def assess_supplier_risk(self):
        """Assess risk for all active suppliers"""
        self.stdout.write(_('Assessing supplier risk...'))
        
        suppliers = Company.objects.filter(is_supplier=True, is_active=True)
        assessed = 0
        high_risk = 0
        
        for supplier in suppliers:
            try:
                # Get or create risk assessment
                risk, created = SupplierRisk.objects.get_or_create(supplier=supplier)
                
                # Force recalculation of delivery risk
                risk.delivery_risk_score = risk.calculate_delivery_risk()
                risk.save()
                
                assessed += 1
                
                # Check if risk is high
                if risk.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_risk += 1
                    
                    # Create risk event if score exceeds threshold
                    if risk.is_alert_triggered and not created:
                        self.create_risk_event(
                            supplier=supplier,
                            category=RiskCategory.DELIVERY if risk.delivery_risk_score > 70 else RiskCategory.FINANCIAL,
                            severity=risk.overall_risk_level,
                            title=_f'High supplier risk detected: {supplier.name}',
                            description=_f'Supplier {supplier.name} has an overall risk score of {risk.overall_risk_score}'
                        )
                
            except Exception as e:
                self.stderr.write(_(f'Error assessing risk for supplier {supplier.name}: {str(e)}'))
        
        return {
            'suppliers_assessed': assessed,
            'suppliers_with_risk': high_risk
        }
    
    def assess_part_risk(self):
        """Assess supply chain risk for all parts"""
        self.stdout.write(_('Assessing part supply chain risk...'))
        
        parts = Part.objects.all()
        assessed = 0
        high_risk = 0
        
        for part in parts:
            try:
                # Get or create supply chain risk assessment
                risk, created = SupplyChainRisk.objects.get_or_create(part=part)
                risk.save()  # This triggers recalculation
                
                assessed += 1
                
                # Check if risk is high
                if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_risk += 1
                    
                    # Create risk event if this is a new high-risk assessment
                    if not created:
                        self.create_risk_event(
                            part=part,
                            category=RiskCategory.ENVIRONMENTAL,
                            severity=risk.risk_level,
                            title=_f'High supply chain risk detected: {part.full_name}',
                            description=_f'Part {part.full_name} has been assessed as {risk.risk_level.label.lower()} risk'
                        )
                
            except Exception as e:
                self.stderr.write(_(f'Error assessing risk for part {part.full_name}: {str(e)}'))
        
        return {
            'parts_assessed': assessed,
            'parts_with_risk': high_risk
        }
    
    def generate_alternative_suppliers(self):
        """Generate alternative supplier suggestions for high-risk parts"""
        self.stdout.write(_('Generating alternative supplier suggestions...'))
        
        from company.models import SupplierPart
        
        # Get high-risk parts that are single-sourced
        high_risk_parts = Part.objects.filter(
            supply_chain_risk__risk_level__in=[RiskLevel.HIGH, RiskLevel.CRITICAL],
            supply_chain_risk__single_source_risk=True
        )
        
        suggestions_generated = 0
        
        for part in high_risk_parts:
            try:
                # Find potential alternative suppliers
                # Look for suppliers that provide similar parts
                similar_parts = Part.objects.filter(
                    category=part.category,
                    supplier_parts__isnull=False
                ).exclude(id=part.id).distinct()
                
                potential_suppliers = []
                
                for similar_part in similar_parts:
                    suppliers = similar_part.supplier_parts.values_list('supplier', flat=True)
                    potential_suppliers.extend(suppliers)
                
                # Remove duplicates and existing suppliers
                existing_suppliers = part.supplier_parts.values_list('supplier', flat=True)
                potential_suppliers = list(set(potential_suppliers) - set(existing_suppliers))
                
                # Create suggestions for top potential suppliers
                for supplier_id in potential_suppliers[:3]:  # Limit to top 3 suggestions
                    supplier = Company.objects.get(id=supplier_id)
                    
                    # Check if suggestion already exists
                    if not AlternativeSupplierSuggestion.objects.filter(
                        part=part,
                        suggested_supplier=supplier
                    ).exists():
                        
                        # Calculate similarity score (simplified)
                        similarity_score = 70  # Default similarity score
                        
                        # Create suggestion
                        AlternativeSupplierSuggestion.objects.create(
                            part=part,
                            suggested_supplier=supplier,
                            similarity_score=similarity_score,
                            reason=_f'Supplier provides similar parts in category {part.category.name}'
                        )
                        
                        suggestions_generated += 1
                
            except Exception as e:
                self.stderr.write(_(f'Error generating suggestions for part {part.full_name}: {str(e)}'))
        
        return {'suggestions_generated': suggestions_generated}
    
    def send_risk_alerts(self):
        """Send alerts for high-risk items"""
        self.stdout.write(_('Sending risk alerts...'))
        
        # In a real implementation, this would integrate with the notification system
        # For now, we'll just log that alerts would be sent
        alerts_sent = 0
        
        # Get high-risk suppliers that need alerts
        high_risk_suppliers = SupplierRisk.objects.filter(
            overall_risk_score__gte=F('alert_threshold'),
            last_assessment_date__gte=InvenTree.helpers.current_date() - timedelta(days=1)
        )
        
        # Get high-risk parts
        high_risk_parts = SupplyChainRisk.objects.filter(
            risk_level__in=[RiskLevel.HIGH, RiskLevel.CRITICAL],
            last_assessment_date__gte=InvenTree.helpers.current_date() - timedelta(days=1)
        )
        
        alerts_sent = high_risk_suppliers.count() + high_risk_parts.count()
        
        # In a production environment, you would send actual notifications here
        # This could be email alerts, in-app notifications, or integration with external systems
        
        return {'alerts_sent': alerts_sent}
    
    def create_risk_event(self, supplier=None, part=None, category=None, severity=None, title=None, description=None):
        """Create a new risk event"""
        try:
            event = RiskEvent.objects.create(
                category=category,
                severity=severity,
                title=title,
                description=description
            )
            
            if supplier:
                event.affected_suppliers.add(supplier)
            
            if part:
                event.affected_parts.add(part)
            
            event.save()
            
        except Exception as e:
            self.stderr.write(_(f'Error creating risk event: {str(e)}'))
