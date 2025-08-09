from rest_framework import serializers
from .models import ProdMast, StckMain, StckDetail

class ProdMastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdMast
        fields = ['id', 'name']

class StckDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StckDetail
        fields = ['id', 'product_id', 'product_name', 'quantity']

class StckMainSerializer(serializers.ModelSerializer):
    details = StckDetailSerializer(many=True, read_only=True)  # relies on related_name='details'

    class Meta:
        model = StckMain
        fields = ['id', 'transaction_type', 'timestamp', 'details']
