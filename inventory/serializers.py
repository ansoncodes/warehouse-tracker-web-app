from rest_framework import serializers
from .models import ProdMast, StckMain, StckDetail

class ProdMastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdMast
        fields = '__all__'

class StckDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StckDetail
        fields = ['product', 'quantity']

class StckMainSerializer(serializers.ModelSerializer):
    details = StckDetailSerializer(many=True)

    class Meta:
        model = StckMain
        fields = '__all__'

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        transaction = StckMain.objects.create(**validated_data)
        for detail in details_data:
            StckDetail.objects.create(transaction=transaction, **detail)
        return transaction