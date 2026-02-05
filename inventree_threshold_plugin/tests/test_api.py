"""Tests for stock threshold plugin API."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from stock.models import StockItem, StockLocation
from part.models import Part

from inventree_threshold_plugin.models import StockItemThreshold


User = get_user_model()


class StockThresholdAPITest(TestCase):
    """Test cases for stock threshold API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)
        
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
        
        # Create stock items
        self.stock_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=100
        )
        
        self.low_stock_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=5
        )
        
        # Create thresholds
        self.threshold_normal = StockItemThreshold.objects.create(
            stock_item=self.stock_item,
            threshold=Decimal('50.00'),
            enabled=True
        )
        
        self.threshold_low = StockItemThreshold.objects.create(
            stock_item=self.low_stock_item,
            threshold=Decimal('10.00'),
            enabled=True
        )
    
    def test_list_thresholds(self):
        """Test listing all thresholds."""
        url = reverse('plugin:stockthreshold:threshold-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_create_threshold(self):
        """Test creating a new threshold."""
        # Create another stock item
        new_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=50
        )
        
        url = reverse('plugin:stockthreshold:threshold-list')
        data = {
            'stock_item': new_item.pk,
            'threshold': '25.00',
            'enabled': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StockItemThreshold.objects.count(), 3)
    
    def test_get_threshold_status(self):
        """Test getting threshold status for a stock item."""
        url = reverse('plugin:stockthreshold:stock-item-threshold-status', 
                      kwargs={'pk': self.low_stock_item.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_threshold'])
        self.assertTrue(response.data['is_low_stock'])
        self.assertEqual(Decimal(response.data['threshold']), Decimal('10.00'))
    
    def test_get_threshold_status_no_threshold(self):
        """Test getting threshold status for stock item without threshold."""
        # Create stock item without threshold
        no_threshold_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=50
        )
        
        url = reverse('plugin:stockthreshold:stock-item-threshold-status',
                      kwargs={'pk': no_threshold_item.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_threshold'])
        self.assertFalse(response.data['is_low_stock'])
    
    def test_get_low_stock_items(self):
        """Test getting all low stock items."""
        url = reverse('plugin:stockthreshold:low-stock-items')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only one item should be below threshold
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['stock_item'], self.low_stock_item.pk)
    
    def test_update_threshold(self):
        """Test updating a threshold."""
        url = reverse('plugin:stockthreshold:threshold-detail',
                      kwargs={'pk': self.threshold_normal.pk})
        data = {
            'threshold': '75.00',
            'enabled': True
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.threshold_normal.refresh_from_db()
        self.assertEqual(self.threshold_normal.threshold, Decimal('75.00'))
    
    def test_delete_threshold(self):
        """Test deleting a threshold."""
        url = reverse('plugin:stockthreshold:threshold-detail',
                      kwargs={'pk': self.threshold_normal.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StockItemThreshold.objects.count(), 1)
