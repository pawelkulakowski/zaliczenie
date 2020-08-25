from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=128, null=False)
    tax_code = models.CharField(max_length=20, null=False)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)


class Addres(models.Model):
    zip_code = models.CharField(max_length=10, null=False)
    city = models.CharField(max_length=64,  null=False)
    address = models.CharField(max_length=64, null=False)
    primary = models.BooleanField(default=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)


class Contact(models.Model):
    name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=False)
    email = models.EmailField()
    position = models.CharField(max_length=64, null=False)
    primary = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
