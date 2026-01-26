"""Initial migration for stock_threshold plugin."""

from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('part', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockThreshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_threshold', models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name='Stock Threshold')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('part', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stock_threshold', to='part.part')),
            ],
            options={
                'unique_together': {('part',)},  
                'verbose_name': 'Stock Threshold',
                'verbose_name_plural': 'Stock Thresholds',
            },
        ),
    ]
