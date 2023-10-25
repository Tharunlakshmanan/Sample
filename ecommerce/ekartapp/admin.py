from django.contrib import admin
#  here importing all the models fo registering
from .models import Product,Contact,OrderUpdate,Orders
# Register your models here.
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(OrderUpdate)
admin.site.register(Orders)