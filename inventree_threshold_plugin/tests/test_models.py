"""Tests for stock threshold plugin models."""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from stock.models import StockItem, StockLocation
from part.models import Part

from inventree_threshold_plugin.models import StockItemThreshold


User = get_user_model()


class StockItemThresholdModelTest(TestCase):
    """Test cases for StockItemThreshold model."""
    
    def setUp(self):
        """Set up test data."""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
        # Create a part
        self.part = Part.objects.create(
            name='Test Part',
            description='A test part',
            component=True,
            trackable=False
        )
        
        # Create a stock location
        self.location = StockLocation.objects.create(
            name='Test Location',
            description='A test location'
        )
        
        # Create a stock item
        self.stock_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=100
        )
        
        # Create a low stock item
        self.low_stock_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=5
        )
    
    def test_threshold_creation(self):
        """Test creating a stock item threshold."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.stock_item,
            threshold=Decimal('10.00'),
            enabled=True
        )
        
        self.assertEqual(threshold.stock_item, self.stock_item)
        self.assertEqual(threshold.threshold, Decimal('10.00'))
        self.assertTrue(threshold.enabled)
        self.assertIsNotNone(threshold.created)
        self.assertIsNotNone(threshold.updated)
    
    def test_is_low_stock_above_threshold(self):
        """Test is_low_stock when quantity is above threshold."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.stock_item,
            threshold=Decimal('50.00'),
            enabled=True
        )
        
        # Stock quantity is 100, threshold is 50
        self.assertFalse(threshold.is_low_stock)
        self.assertEqual(threshold.quantity_below_threshold, 0)
    
    def test_is_low_stock_below_threshold(self):
        """Test is_low_stock when quantity is below threshold."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.low_stock_item,
            threshold=Decimal('10.00'),
            enabled=True
        )
        
        # Stock quantity is 5, threshold is 10
        self.assertTrue(threshold.is_low_stock)
        self.assertEqual(threshold.quantity_below_threshold, Decimal('5.00'))
    
    def test_is_low_stock_disabled(self):
        """Test is_low_stock when threshold is disabled."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.low_stock_item,
            threshold=Decimal('10.00'),
            enabled=False
        )
        
        # Even though stock is below threshold, it's disabled
        self.assertFalse(threshold.is_low_stock)
    
    def test_string_representation(self):
        """Test the string representation of threshold."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.stock_item,
            threshold=Decimal('25.00'),
            enabled=True
        )
        
        expected_str = f"{self.part.name} - Threshold: 25.00"
        self.assertEqual(str(threshold), expected_str)
    
    def test_one_to_one_relationship(self):
        """Test that stock item has one threshold config."""
        threshold = StockItemThreshold.objects.create(
            stock_item=self.stock_item,
            threshold=Decimal('20.00'),
            enabled=True
        )
        
        # Access threshold from stock item
        self.assertEqual(self.stock_item.threshold_config, threshold)
        
        # Attempting to create another threshold should raise an error
        with self.assertRaises(Exception):
            StockItemThreshold.objects.create(
                stock_item=self.stock_item,
                threshold=Decimal('30.00'),
                enabled=True
            )
