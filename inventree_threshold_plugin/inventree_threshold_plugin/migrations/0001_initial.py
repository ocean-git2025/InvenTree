# Generated initial migration for Stock Threshold Plugin

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Initial migration for stock threshold plugin."""

    initial = True

    dependencies = [
        ('stock', '0116_alter_stockitem_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockItemThreshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threshold', models.DecimalField(decimal_places=5, default=0, help_text='Minimum stock quantity before low stock warning is triggered', max_digits=15, verbose_name='Threshold')),
                ('enabled', models.BooleanField(default=True, help_text='Enable threshold checking for this stock item', verbose_name='Enabled')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('stock_item', models.OneToOneField(help_text='The stock item this threshold applies to', on_delete=django.db.models.deletion.CASCADE, related_name='threshold_config', to='stock.stockitem', verbose_name='Stock Item')),
            ],
            options={
                'verbose_name': 'Stock Item Threshold',
                'verbose_name_plural': 'Stock Item Thresholds',
            },
        ),
    ]
