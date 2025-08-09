from urllib.parse import unquote

from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProdMast, StckMain, StckDetail
from .serializers import StckMainSerializer

class StckMainViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/transactions/ - list all transactions with nested details
    """
    queryset = StckMain.objects.all().order_by('-timestamp').prefetch_related(
        Prefetch('details', queryset=StckDetail.objects.select_related('product'))
    )
    serializer_class = StckMainSerializer
    permission_classes = [AllowAny]

class InventorySummaryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Simple summary: product name -> total stock (IN minus OUT)
        # Adjust if you have a more elaborate summary view already.
        from django.db.models import Sum, Case, When, IntegerField, F, Value as V

        # Total IN per product
        ins = StckDetail.objects.filter(
            transaction__transaction_type='IN'
        ).values('product__id', 'product__name').annotate(total_in=Sum('quantity'))

        # Total OUT per product
        outs = StckDetail.objects.filter(
            transaction__transaction_type='OUT'
        ).values('product__id', 'product__name').annotate(total_out=Sum('quantity'))

        # Merge ins and outs by product id
        totals = {}
        for row in ins:
            pid = row['product__id']
            totals[pid] = {
                'product_id': pid,
                'product': row['product__name'],
                'in_qty': row['total_in'] or 0,
                'out_qty': 0,
            }
        for row in outs:
            pid = row['product__id']
            if pid not in totals:
                totals[pid] = {
                    'product_id': pid,
                    'product': row['product__name'],
                    'in_qty': 0,
                    'out_qty': row['total_out'] or 0,
                }
            else:
                totals[pid]['out_qty'] = row['total_out'] or 0

        # Convert to list with current_stock
        result = []
        for v in totals.values():
            result.append({
                'product_id': v['product_id'],
                'product': v['product'],
                'in_qty': v['in_qty'],
                'out_qty': v['out_qty'],
                'current_stock': (v['in_qty'] - v['out_qty']),
            })

        return Response(result)

@api_view(['GET'])
@permission_classes([AllowAny])
def product_transaction_history(request, product_name):
    """
    Returns transactions for a given product name with details scoped to that product.
    Response shape matches frontend expectations:
    [
      {
        "id": 1,
        "transaction_type": "IN",
        "timestamp": "2025-08-09T10:00:00Z",
        "details": [
          {"product_id": 3, "product_name": "Razer Viper Mini", "quantity": 5}
        ]
      },
      ...
    ]
    """
    try:
        decoded_name = unquote(product_name or '').strip()
        if not decoded_name:
            return Response({"error": "Product name is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = ProdMast.objects.get(name=decoded_name)
        except ProdMast.DoesNotExist:
            return Response({"error": f"Product '{decoded_name}' not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get all transactions that include this product in their details
        transactions = (
            StckMain.objects.filter(details__product=product)
            .distinct()
            .order_by('-timestamp')
            .prefetch_related(
                Prefetch(
                    'details',
                    queryset=StckDetail.objects.filter(product=product).select_related('product')
                )
            )
        )

        # Serialize using the existing serializer (details limited via Prefetch)
        serializer = StckMainSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Avoid exposing internals but log server-side if possible
        return Response({"error": "Error fetching transaction history."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
