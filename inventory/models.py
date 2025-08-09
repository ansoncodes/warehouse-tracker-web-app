from django.db import models


class ProdMast(models.Model):
    name = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class StckMain(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    )
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} #{self.id} @ {self.timestamp}"


class StckDetail(models.Model):
    transaction = models.ForeignKey(StckMain, related_name='details', on_delete=models.CASCADE)
    product = models.ForeignKey(ProdMast, on_delete=models.CASCADE)
    quantity = models.IntegerField()
