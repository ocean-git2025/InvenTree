"""
Unit tests for Stock Threshold Plugin.

These tests verify the plugin's functionality including:
- Plugin settings
- Threshold storage in StockItem metadata
- Threshold checking logic
- UI panel generation
"""

from decimal import Decimal

from django.test import TestCase

from InvenTree.unit_test import InvenTreeTestCase
from part.models import Part
from stock.models import StockItem, StockLocation


class StockThresholdPluginTests(InvenTreeTestCase):
    """Tests for StockThresholdPlugin."""

    def setUp(self):
        """Set up test data."""
        super().setUp()

        # Create test part
        self.part = Part.objects.create(
            name='Test Part for Threshold',
            description='Test Description',
            active=True,
        )

        # Create test location
        self.location = StockLocation.objects.create(
            name='Test Location for Threshold',
        )

        # Create test stock item
        self.stock_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=Decimal('10'),
        )

    def _get_plugin(self):
        """Get the plugin instance from registry."""
        from plugin import registry

        # Ensure plugin is enabled
        registry.set_plugin_state('stock-threshold', True)
        plugin = registry.get_plugin('stock-threshold')
        return plugin

    def test_plugin_installed(self):
        """Test that the plugin is installed and can be activated."""
        from plugin import registry

        registry.set_plugin_state('stock-threshold', True)
        plugin = registry.get_plugin('stock-threshold')

        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.SLUG, 'stock-threshold')
        self.assertEqual(plugin.VERSION, '1.0.0')

    def test_plugin_settings_defined(self):
        """Test plugin settings are correctly defined."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        self.assertIn('ENABLE_THRESHOLD_WARNING', plugin.settings)
        self.assertIn('DEFAULT_THRESHOLD', plugin.settings)
        self.assertIn('WARNING_COLOR', plugin.settings)
        self.assertIn('ENABLE_PANEL', plugin.settings)

    def test_default_threshold_setting(self):
        """Test default threshold setting value."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        default_threshold = plugin.get_setting('DEFAULT_THRESHOLD')
        self.assertEqual(default_threshold, 0)

    def test_get_stock_item_threshold_default(self):
        """Test getting threshold for stock item without custom threshold."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        threshold = plugin.get_stock_item_threshold(self.stock_item)
        self.assertEqual(threshold, 0)

    def test_set_and_get_custom_threshold(self):
        """Test setting and getting custom threshold for stock item."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Set custom threshold
        plugin.set_stock_item_threshold(self.stock_item, 10)

        # Refresh from database
        self.stock_item.refresh_from_db()

        # Get threshold
        threshold = plugin.get_stock_item_threshold(self.stock_item)
        self.assertEqual(threshold, 10)

    def test_is_below_threshold_true(self):
        """Test checking if stock item is below threshold (should be True)."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Set threshold higher than quantity
        plugin.set_stock_item_threshold(self.stock_item, 15)
        self.stock_item.refresh_from_db()

        self.assertTrue(plugin.is_below_threshold(self.stock_item))

    def test_is_below_threshold_false(self):
        """Test checking if stock item is below threshold (should be False)."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Set threshold lower than quantity
        plugin.set_stock_item_threshold(self.stock_item, 5)
        self.stock_item.refresh_from_db()

        self.assertFalse(plugin.is_below_threshold(self.stock_item))

    def test_is_below_threshold_equal(self):
        """Test checking if stock item is below threshold when equal."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Set threshold equal to quantity
        plugin.set_stock_item_threshold(self.stock_item, 10)
        self.stock_item.refresh_from_db()

        # Equal should not be "below"
        self.assertFalse(plugin.is_below_threshold(self.stock_item))

    def test_metadata_stored_correctly(self):
        """Test that threshold is stored in the correct metadata key."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        plugin.set_stock_item_threshold(self.stock_item, 20)
        self.stock_item.refresh_from_db()

        # Check metadata directly
        metadata = self.stock_item.get_metadata('stock-threshold', {})
        self.assertIn('threshold', metadata)
        self.assertEqual(metadata['threshold'], 20)

    def test_metadata_persistence(self):
        """Test that threshold metadata persists across saves."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        plugin.set_stock_item_threshold(self.stock_item, 25)

        # Modify something else and save
        self.stock_item.notes = 'Updated notes'
        self.stock_item.save()
        self.stock_item.refresh_from_db()

        # Threshold should still be there
        threshold = plugin.get_stock_item_threshold(self.stock_item)
        self.assertEqual(threshold, 25)

    def test_ui_panels_disabled(self):
        """Test UI panels when panel setting is disabled."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Disable panels
        plugin.set_setting('ENABLE_PANEL', False)

        context = {
            'target_model': 'stockitem',
            'target_id': self.stock_item.pk,
        }

        panels = plugin.get_ui_panels(None, context)
        self.assertEqual(len(panels), 0)

    def test_ui_panels_enabled(self):
        """Test UI panels when panel setting is enabled."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Enable panels
        plugin.set_setting('ENABLE_PANEL', True)

        context = {
            'target_model': 'stockitem',
            'target_id': self.stock_item.pk,
        }

        panels = plugin.get_ui_panels(None, context)
        self.assertEqual(len(panels), 1)
        self.assertEqual(panels[0]['key'], 'threshold-panel')

    def test_ui_panels_context_data(self):
        """Test UI panels context data contains correct values."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        plugin.set_setting('ENABLE_PANEL', True)
        plugin.set_stock_item_threshold(self.stock_item, 5)

        context = {
            'target_model': 'stockitem',
            'target_id': self.stock_item.pk,
        }

        panels = plugin.get_ui_panels(None, context)
        self.assertEqual(len(panels), 1)

        panel_context = panels[0]['context']
        self.assertEqual(panel_context['threshold'], 5)
        self.assertEqual(panel_context['quantity'], 10.0)
        self.assertFalse(panel_context['is_below_threshold'])

    def test_ui_panels_wrong_model(self):
        """Test UI panels return empty for wrong model."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        plugin.set_setting('ENABLE_PANEL', True)

        context = {
            'target_model': 'part',
            'target_id': self.part.pk,
        }

        panels = plugin.get_ui_panels(None, context)
        self.assertEqual(len(panels), 0)

    def test_get_low_stock_items(self):
        """Test getting list of low stock items."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Create another stock item
        stock_item2 = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=Decimal('2'),
        )

        # Set thresholds
        plugin.set_stock_item_threshold(self.stock_item, 5)  # 10 > 5, OK
        plugin.set_stock_item_threshold(stock_item2, 10)  # 2 < 10, LOW

        self.stock_item.refresh_from_db()
        stock_item2.refresh_from_db()

        low_stock_pks = plugin.get_low_stock_items()

        self.assertIn(stock_item2.pk, low_stock_pks)
        self.assertNotIn(self.stock_item.pk, low_stock_pks)

    def test_spotlight_actions(self):
        """Test spotlight actions are returned."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        actions = plugin.get_ui_spotlight_actions(None, {})
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['key'], 'view-low-stock')

    def test_threshold_with_zero_quantity(self):
        """Test threshold check with zero quantity."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Create item with zero quantity
        zero_item = StockItem.objects.create(
            part=self.part,
            location=self.location,
            quantity=Decimal('0'),
        )

        plugin.set_stock_item_threshold(zero_item, 5)
        zero_item.refresh_from_db()

        self.assertTrue(plugin.is_below_threshold(zero_item))

    def test_multiple_metadata_keys(self):
        """Test that plugin metadata doesn't interfere with other metadata."""
        plugin = self._get_plugin()
        self.assertIsNotNone(plugin)

        # Set some other metadata
        self.stock_item.set_metadata('other-plugin', {'data': 'value'})

        # Set threshold
        plugin.set_stock_item_threshold(self.stock_item, 15)

        self.stock_item.refresh_from_db()

        # Both should exist
        self.assertEqual(
            self.stock_item.get_metadata('other-plugin'), {'data': 'value'}
        )
        self.assertEqual(
            self.stock_item.get_metadata('stock-threshold'), {'threshold': 15}
        )
