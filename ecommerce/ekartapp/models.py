from typing import Any
from django.db import models

# Create your models here.
# first we create a contact table
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    desc=models.TextField(max_length=500)
    phonenumber=models.CharField(max_length=12)
    # this init method is going to generate number sequence
    # def __init__(self):
    #     return self.id
    
# make sure the module pillow installed, pillow module used to access image
class Product(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=100)
    category=models.CharField(max_length=100,default="")
    # it means it will allows blank and null values
    subcategory=models.CharField(max_length=100,blank=True,null=True)
    price=models.IntegerField(default=0)
    actual_price=models.IntegerField(default=0)
    stock=models.IntegerField(default=0,blank=True,null=True)
    desc=models.TextField(max_length=500)
    image=models.ImageField(upload_to="Products")

    def __str__(self):
        return self.product_name
    
class Orders(models.Model):
    order_id=models.AutoField(primary_key=True)
    items_json=models.CharField(max_length=5000)
    amount=models.IntegerField(default=0)
    name=models.CharField(max_length=100)
    email=models.EmailField()
    address1=models.CharField(max_length=100)
    address2=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    zipcode=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    oid=models.CharField(max_length=12,blank=True,null=True)
    amount_paid=models.CharField(default=0,max_length=12,blank=True,null=True)
    payment_status=models.CharField(default="Unpaid",max_length=12,blank=True,null=True)
    profit=models.IntegerField(default=0,blank=True,null=True)
    timestamp=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default="")
    update_des=models.CharField(max_length=1000)
    delivered=models.BooleanField(default=False)
    timestamp=models.DateField(auto_now_add=True)

    def __int__(self):
        return self.order_id
    