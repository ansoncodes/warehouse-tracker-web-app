from django.shortcuts import render
from rest_framework import viewsets
from .models import ProdMast, StckMain
from .serializers import ProdMastSerializer, StckMainSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Case, When, F
from .models import StckDetail
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import unquote



class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProdMast.objects.all()
    serializer_class = ProdMastSerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = ProdMast.objects.all()
    serializer_class = ProdMastSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = StckMain.objects.all()
    serializer_class = StckMainSerializer

@api_view(['GET'])
def inventory_view(request):
    data = (
        StckDetail.objects.values('product__name')
        .annotate(
            stock_in=Sum(Case(When(transaction__transaction_type='IN', then=F('quantity')))),
            stock_out=Sum(Case(When(transaction__transaction_type='OUT', then=F('quantity'))))
        )
    )

    inventory = [
        {
            "product": item["product__name"],
            "available_quantity": (item["stock_in"] or 0) - (item["stock_out"] or 0)
        } for item in data
    ]
    return Response(inventory)


class InventorySummaryView(APIView):
    def get(self, request):
        inventory = []
        products = ProdMast.objects.all()

        for product in products:
            total_in = StckDetail.objects.filter(product=product, transaction__transaction_type='IN').aggregate(Sum('quantity'))['quantity__sum'] or 0
            total_out = StckDetail.objects.filter(product=product, transaction__transaction_type='OUT').aggregate(Sum('quantity'))['quantity__sum'] or 0
            current_stock = total_in - total_out

            inventory.append({
                "product": product.name,
                "sku": product.sku,
                "current_stock": current_stock
            })

        return Response(inventory)


@api_view(['GET'])
def product_transaction_history(request, product_name):
    """
    Get transaction history for a specific product by product name
    """
    try:
        
        decoded_product_name = unquote(product_name)
        
        
        try:
            product = ProdMast.objects.get(name=decoded_product_name)
        except ProdMast.DoesNotExist:
            return Response(
                {"error": f"Product '{decoded_product_name}' not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
       
        transactions = StckMain.objects.filter(
            stckdetail__product=product
        ).distinct().order_by('-created_at')
        
        transaction_history = []
        
        for transaction in transactions:
            
            product_details = StckDetail.objects.filter(
                transaction=transaction,
                product=product
            )
            
            
            transaction_data = {
                'id': transaction.id,
                'transaction_type': transaction.transaction_type,
                'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
                'notes': getattr(transaction, 'notes', ''),  
                'details': [
                    {
                        'product_id': detail.product.id,
                        'product_name': detail.product.name,
                        'quantity': detail.quantity
                    }
                    for detail in product_details
                ]
            }
            transaction_history.append(transaction_data)
        
        return Response(transaction_history)
        
    except Exception as e:
        return Response(
            {"error": f"Error fetching transaction history: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class StckMainViewSet(viewsets.ModelViewSet):
    queryset = StckMain.objects.all()
    serializer_class = StckMainSerializer

    def create(self, request, *args, **kwargs):
        print("➡️ Incoming /api/transactions/ POST:", request.data)
        return super().create(request, *args, **kwargs)

summary = (
    StckDetail.objects.values('product__id')
    .annotate(total_qty=Sum('quantity'))
    .order_by('product__id')
)