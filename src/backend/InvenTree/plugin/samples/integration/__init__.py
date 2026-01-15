"""Integration plugin samples."""

from plugin.samples.integration.another_sample import AnotherSamplePlugin
from plugin.samples.integration.api_caller import SampleAPICaller
from plugin.samples.integration.label_sample import LabelSamplePlugin
from plugin.samples.integration.report_plugin_sample import ReportPluginSample
from plugin.samples.integration.sample import SampleIntegrationPlugin
from plugin.samples.integration.sample_currency_exchange import SampleCurrencyExchangePlugin
from plugin.samples.integration.scheduled_task import ScheduledTaskSamplePlugin
from plugin.samples.integration.simpleactionplugin import SimpleActionPlugin
from plugin.samples.integration.stock_threshold_plugin import StockThresholdPlugin
from plugin.samples.integration.transition import SampleTransitions
from plugin.samples.integration.user_interface_sample import SampleUserInterfacePlugin
from plugin.samples.integration.validation_sample import ValidationSamplePlugin

__all__ = [
    'AnotherSamplePlugin',
    'SampleAPICaller',
    'SampleIntegrationPlugin',
    'SampleCurrencyExchangePlugin',
    'SimpleActionPlugin',
    'ScheduledTaskSamplePlugin',
    'SampleUserInterfacePlugin',
    'ValidationSamplePlugin',
    'SampleTransitions',
    'LabelSamplePlugin',
    'ReportPluginSample',
    'StockThresholdPlugin',
]
