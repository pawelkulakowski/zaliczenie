from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=128, null=False)
    tax_code = models.CharField(max_length=20, null=False)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)


class Address(models.Model):
    zip_code = models.CharField(max_length=10, null=False)
    city = models.CharField(max_length=64,  null=False)
    address = models.CharField(max_length=64, null=False)
    primary = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)


class Contact(models.Model):
    name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=False)
    email = models.EmailField(null=True)
    position = models.CharField(max_length=64, null=True)
    primary = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)


class User(models.Model):
    POSITIONS = (
        ('S', 'Sprzedawca'),
        ('SB', 'Sprzedawca/Biuro'),
        ('B', 'Biuro'),
        ('D', 'Dyrektor')
    )
    name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=False)
    email = models.EmailField(null=True)
    position = models.CharField(choices=POSITIONS, null=False, max_length=3)


class Offer(models.Model):
    STATUS = (

    )
    signature = models.CharField(max_length=64, null=False)
    createdBy = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='createdBy')
    comments = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=1)
    expirationDate = models.DateField(null=False)
    customerContact = models.ForeignKey(Contact, null=True, on_delete=models.SET_NULL)
    customerAddress = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    itemsCount = models.IntegerField(null=True)
    calculationUser = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='calculationUser')
