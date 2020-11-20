from django.contrib import admin

from .models import Product, ProductReleaseHistory, TargetSite


admin.site.register(Product)
admin.site.register(ProductReleaseHistory)
admin.site.register(TargetSite)
