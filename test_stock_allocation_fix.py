"""Test script to verify stock allocation sync with proper Django setup."""

import os
import sys
import django
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / 'src' / 'backend' / 'InvenTree'
sys.path.insert(0, str(backend_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'InvenTree.settings')

# Initialize Django
try:
    django.setup()
    print("✓ Django initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Django: {e}")
    sys.exit(1)

# Now import models after Django is setup
from decimal import Decimal
from stock.models import StockItem, StockLocation
from part.models import Part
from order.models import SalesOrder, SalesOrderLineItem, SalesOrderAllocation
from company.models import Company

def test_stock_allocation_sync():
    """Test that stock item quantity changes sync with sales order allocations."""
    
    print("\n" + "="*60)
    print("Testing Stock Allocation Sync Functionality")
    print("="*60)
    
    try:
        # Create test data
        print("\n1. Creating test data...")
        
        # Get or create a part
        part, created = Part.objects.get_or_create(
            name='Test Part for Allocation Sync',
            defaults={
                'description': 'Test part for allocation sync',
                'active': True,
                'purchaseable': True,
                'salable': True,
                'assembly': False,
                'component': False,
                'trackable': False,
                'purchaseable': True,
            }
        )
        print(f"   {'Created' if created else 'Found'} part: {part.name}")
        
        # Get or create a location
        location, created = StockLocation.objects.get_or_create(
            name='Test Location for Allocation Sync',
            defaults={'description': 'Test location for allocation sync'}
        )
        print(f"   {'Created' if created else 'Found'} location: {location.name}")
        
        # Create a stock item
        stock_item = StockItem.objects.create(
            part=part,
            quantity=Decimal('100'),
            location=location
        )
        print(f"   Created stock item with quantity: {stock_item.quantity}")
        
        # Get or create a company
        company, created = Company.objects.get_or_create(
            name='Test Company for Allocation Sync',
            defaults={'description': 'Test company for allocation sync'}
        )
        print(f"   {'Created' if created else 'Found'} company: {company.name}")
        
        # Create a sales order
        sales_order = SalesOrder.objects.create(
            customer=company,
            reference='SO-TEST-001',
            status=10
        )
        print(f"   Created sales order: {sales_order.reference}")
        
        # Create a line item
        line_item = SalesOrderLineItem.objects.create(
            order=sales_order,
            part=part,
            quantity=Decimal('50')
        )
        print(f"   Created line item with quantity: {line_item.quantity}")
        
        # Create allocation
        allocation = SalesOrderAllocation.objects.create(
            line=line_item,
            item=stock_item,
            quantity=Decimal('30')
        )
        print(f"   Created allocation with quantity: {allocation.quantity}")
        
        # Verify initial state
        assert allocation.quantity == Decimal('30'), "Initial allocation quantity should be 30"
        assert stock_item.quantity == Decimal('100'), "Initial stock quantity should be 100"
        print("\n✓ Initial state verified")
        
        # Test 1: Decrease stock quantity below allocated amount
        print("\n2. Test 1: Decreasing stock quantity from 100 to 25...")
        stock_item.quantity = Decimal('25')
        stock_item.save()
        
        # Refresh allocation from database
        allocation.refresh_from_db()
        
        # Allocation should be reduced to fit within new quantity
        assert allocation.quantity == Decimal('25'), f"Allocation should be reduced to 25, but got {allocation.quantity}"
        print(f"   Stock quantity: {stock_item.quantity}")
        print(f"   Allocation quantity: {allocation.quantity}")
        print("✓ Allocation correctly reduced to 25")
        
        # Test 2: Increase stock quantity
        print("\n3. Test 2: Increasing stock quantity from 25 to 150...")
        stock_item.quantity = Decimal('150')
        stock_item.save()
        
        # Refresh allocation from database
        allocation.refresh_from_db()
        
        # Allocation should remain unchanged
        assert allocation.quantity == Decimal('25'), f"Allocation should remain 25, but got {allocation.quantity}"
        print(f"   Stock quantity: {stock_item.quantity}")
        print(f"   Allocation quantity: {allocation.quantity}")
        print("✓ Allocation correctly remained at 25")
        
        # Test 3: Multiple allocations
        print("\n4. Test 3: Testing with multiple allocations...")
        allocation2 = SalesOrderAllocation.objects.create(
            line=line_item,
            item=stock_item,
            quantity=Decimal('40')
        )
        print(f"   Created second allocation with quantity: {allocation2.quantity}")
        
        # Decrease stock quantity significantly
        stock_item.quantity = Decimal('30')
        stock_item.save()
        
        # Refresh allocations from database
        allocation.refresh_from_db()
        allocation2.refresh_from_db()
        
        # First allocation should be reduced, second should be deleted
        assert allocation.quantity == Decimal('30'), f"First allocation should be 30, but got {allocation.quantity}"
        assert not SalesOrderAllocation.objects.filter(pk=allocation2.pk).exists(), "Second allocation should be deleted"
        print(f"   Stock quantity: {stock_item.quantity}")
        print(f"   First allocation quantity: {allocation.quantity}")
        print(f"   Second allocation exists: {SalesOrderAllocation.objects.filter(pk=allocation2.pk).exists()}")
        print("✓ Multiple allocations handled correctly")
        
        # Clean up
        print("\n5. Cleaning up test data...")
        allocation.delete()
        line_item.delete()
        sales_order.delete()
        stock_item.delete()
        print("✓ Test data cleaned up")
        
        print("\n" + "="*60)
        print("✓ All tests passed successfully!")
        print("="*60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Assertion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_stock_allocation_sync()
    sys.exit(0 if success else 1)