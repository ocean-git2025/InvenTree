"""Simple test script to verify stock allocation sync functionality."""

import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'backend', 'InvenTree'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')
django.setup()

from decimal import Decimal
from stock.models import StockItem, StockLocation
from part.models import Part
from order.models import SalesOrder, SalesOrderLineItem, SalesOrderAllocation
from company.models import Company

def test_stock_allocation_sync():
    """Test that stock item quantity changes sync with sales order allocations."""
    
    print("Testing stock allocation sync functionality...")
    
    # Create test data
    try:
        # Get or create a part
        part, _ = Part.objects.get_or_create(
            name='Test Part',
            defaults={
                'description': 'Test part for allocation sync',
                'active': True,
                'purchaseable': True,
                'salable': True
            }
        )
        
        # Get or create a location
        location, _ = StockLocation.objects.get_or_create(
            name='Test Location',
            defaults={'description': 'Test location for allocation sync'}
        )
        
        # Create a stock item
        stock_item = StockItem.objects.create(
            part=part,
            quantity=Decimal('100'),
            location=location
        )
        
        print(f"Created stock item with quantity: {stock_item.quantity}")
        
        # Get or create a company
        company, _ = Company.objects.get_or_create(
            name='Test Company',
            defaults={'description': 'Test company for allocation sync'}
        )
        
        # Create a sales order
        sales_order = SalesOrder.objects.create(
            customer=company,
            reference='SO-TEST-001',
            status=10
        )
        
        print(f"Created sales order: {sales_order.reference}")
        
        # Create a line item
        line_item = SalesOrderLineItem.objects.create(
            order=sales_order,
            part=part,
            quantity=Decimal('50')
        )
        
        print(f"Created line item with quantity: {line_item.quantity}")
        
        # Create allocation
        allocation = SalesOrderAllocation.objects.create(
            line=line_item,
            item=stock_item,
            quantity=Decimal('30')
        )
        
        print(f"Created allocation with quantity: {allocation.quantity}")
        
        # Verify initial state
        assert allocation.quantity == Decimal('30'), "Initial allocation quantity should be 30"
        assert stock_item.quantity == Decimal('100'), "Initial stock quantity should be 100"
        print("✓ Initial state verified")
        
        # Test 1: Decrease stock quantity below allocated amount
        print("\nTest 1: Decreasing stock quantity from 100 to 25...")
        stock_item.quantity = Decimal('25')
        stock_item.save()
        
        # Refresh allocation from database
        allocation.refresh_from_db()
        
        # Allocation should be reduced to fit within new quantity
        assert allocation.quantity == Decimal('25'), f"Allocation should be reduced to 25, but got {allocation.quantity}"
        print("✓ Allocation correctly reduced to 25")
        
        # Test 2: Increase stock quantity
        print("\nTest 2: Increasing stock quantity from 25 to 150...")
        stock_item.quantity = Decimal('150')
        stock_item.save()
        
        # Refresh allocation from database
        allocation.refresh_from_db()
        
        # Allocation should remain unchanged
        assert allocation.quantity == Decimal('25'), f"Allocation should remain 25, but got {allocation.quantity}"
        print("✓ Allocation correctly remained at 25")
        
        # Clean up
        allocation.delete()
        line_item.delete()
        sales_order.delete()
        stock_item.delete()
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_stock_allocation_sync()
    sys.exit(0 if success else 1)