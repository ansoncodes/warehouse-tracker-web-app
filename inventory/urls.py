from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='products')
router.register(r'transactions', views.StckMainViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
    path('inventory-summary/', views.InventorySummaryView.as_view(), name='inventory-summary'),
    path('transactions/history/<str:product_name>/', views.product_transaction_history, name='product-transaction-history'),
]
