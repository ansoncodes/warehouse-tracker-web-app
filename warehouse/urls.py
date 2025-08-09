from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),      # adds endpoints at /
    path('api/', include('inventory.urls')),  # still keeps /api/
]
