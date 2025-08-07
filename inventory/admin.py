from django.contrib import admin

# Register your models here.
from .models import StckMain, StckDetail

admin.site.register(StckMain)
admin.site.register(StckDetail) 