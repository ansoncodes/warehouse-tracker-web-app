from rest_framework import serializers
from .models import ProdMast, StckMain, StckDetail


class ProdMastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdMast
        fields = ['id', 'name', 'sku', 'description']


class StckDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StckDetail
        fields = ['id', 'product_id', 'product_name', 'quantity']


class StckMainSerializer(serializers.ModelSerializer):
    details = StckDetailSerializer(many=True, read_only=True)

    class Meta:
        model = StckMain
        fields = ['id', 'transaction_type', 'timestamp', 'details']


# For creating transactions
class StckDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StckDetail
        fields = ['product', 'quantity']


class StckMainCreateSerializer(serializers.ModelSerializer):
    details = StckDetailCreateSerializer(many=True)

    class Meta:
        model = StckMain
        fields = ['transaction_type', 'details']

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        tx = StckMain.objects.create(**validated_data)
        for d in details_data:
            StckDetail.objects.create(transaction=tx, **d)
        return tx
