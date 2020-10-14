from django.db import models
from opakowania import validators
from django import forms


class Customer(models.Model):
    customer_name = models.CharField(
        max_length=128, null=False, verbose_name="Nazwa klienta"
    )
    tax_code = models.CharField(
        max_length=10, null=False, verbose_name="NIP", unique=True
    )
    description = models.TextField(verbose_name="Opis", blank=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name}, NIP: {self.tax_code}"

    def get_primary_address(self):
        return Address.objects.filter(customer=self).filter(primary=True).first()

    def get_primary_contact(self):
        return Contact.objects.filter(customer=self).filter(primary=True).first()


class Address(models.Model):
    zip_code = models.CharField(max_length=10, null=False, verbose_name="Kod pocztowy")
    city = models.CharField(max_length=64, null=False, verbose_name="Miejscowość")
    address = models.CharField(max_length=64, null=False, verbose_name="Adres")
    primary = models.BooleanField(default=False, verbose_name="Główny")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.address}, {self.zip_code}, {self.city} {", Adres główny" if self.primary else ""}'


class AddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.address}, {obj.city}, {obj.zip_code}'


class Contact(models.Model):
    name = models.CharField(max_length=128, null=False, verbose_name="Imię i nazwisko")
    phone = models.CharField(max_length=64, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Email")
    position = models.CharField(max_length=64, null=True, verbose_name="Stanowisko")
    primary = models.BooleanField(default=False, verbose_name="Główny")
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f'{self.name}, {self.position} {", Kontak główny" if self.primary else ""}'
        )


class ConatactChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}, {obj.position} {', tel.: ' + obj.phone if obj.phone != '' else ''} {', email: ' + obj.email if obj.email != '' else ''}"


class User(models.Model):
    POSITIONS = (
        ("S", "Sprzedawca"),
        ("SB", "Sprzedawca/Biuro"),
        ("B", "Biuro"),
        ("D", "Dyrektor"),
    )
    name = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=64, null=False)
    email = models.EmailField(null=True)
    position = models.CharField(choices=POSITIONS, null=False, max_length=3)


class Offer(models.Model):
    STATUS = ((1, "Nowa"),)
    signature = models.CharField(max_length=64, null=False)
    createdBy = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="createdBy"
    )
    comments = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=1)
    # expirationDate = models.DateField(null=False)
    customerContact = models.ForeignKey(Contact, null=True, on_delete=models.SET_NULL)
    customerAddress = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=False, on_delete=models.PROTECT)
    itemsCount = models.IntegerField(null=True, default=0)
    calculationUser = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="calculationUser"
    )
