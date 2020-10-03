from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=128, null=False, verbose_name='Nazwa klienta')
    tax_code = models.CharField(max_length=20, null=False, verbose_name='NIP')
    description = models.TextField(verbose_name='Opis')
    created = models.DateField(auto_now_add=True)


class Address(models.Model):
    zip_code = models.CharField(max_length=10, null=False, verbose_name='Kod pocztowy')
    city = models.CharField(max_length=64,  null=False, verbose_name='Miejscowość')
    address = models.CharField(max_length=64, null=False, verbose_name='Adres')
    primary = models.BooleanField(default=False, verbose_name='Główny')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Contact(models.Model):
    name = models.CharField(max_length=128, null=False, verbose_name='Imię i nazwisko')
    phone = models.CharField(max_length=64, null=False, verbose_name='Telefon')
    email = models.EmailField(null=True, verbose_name='Email')
    position = models.CharField(max_length=64, null=True, verbose_name='Stanowisko')
    primary = models.BooleanField(default=False, verbose_name='Główny')
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)


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
