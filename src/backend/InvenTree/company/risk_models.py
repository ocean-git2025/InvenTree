from django.db import models
from django.utils.translation import gettext_lazy as _
from InvenTree.models import InvenTreeModel
from .models import Company, SupplierPart


class RiskLevel(models.TextChoices):
    