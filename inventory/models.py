from django.db import models

# Create your models here.

class ProdMast(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

class StckMain(models.Model): 
    TRANSACTION_TYPES = [('IN', 'Stock In'), ('OUT', 'Stock Out')]
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

class StckDetail(models.Model): 
    transaction = models.ForeignKey(StckMain, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(ProdMast, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
