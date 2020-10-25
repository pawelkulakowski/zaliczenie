from django.db import models
from opakowania import validators
from django import forms
from datetime import date
from django.utils import timezone, dateformat
from django.db.models import F


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

    def ordered_offer_set(self):
        return self.offer_set.order_by("-lastModified")


class Address(models.Model):
    zip_code = models.CharField(max_length=10, null=False, verbose_name="Kod pocztowy")
    city = models.CharField(max_length=64, null=False, verbose_name="Miejscowość")
    address = models.CharField(max_length=64, null=False, verbose_name="Adres")
    primary = models.BooleanField(default=False, verbose_name="Główny")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.address}, {self.zip_code}, {self.city}'


class AddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.address}, {obj.city}, {obj.zip_code}"


class Contact(models.Model):
    name = models.CharField(max_length=128, null=False, verbose_name="Imię i nazwisko")
    phone = models.CharField(max_length=64, blank=True, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Email")
    position = models.CharField(max_length=64, null=True, verbose_name="Stanowisko")
    primary = models.BooleanField(default=False, verbose_name="Główny")
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return (
            f'{self.name}, {self.position}'
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
    def now_plus_month():
        return dateformat.format(timezone.now() + timezone.timedelta(days=30), "Y-m-d")

    def get_positions_count(self):
        return Position.objects.filter(offer=self).count()

    def get_product_count(self):
        count = 0
        positions = Position.objects.filter(offer=self)
        for pos in positions:
            count += pos.numberOfProducts
        return count

    def add_position(self):
        self.numberOfPositions += 1
        self.activePositions += 1
        self.save()
        return self.numberOfPositions

    def remove_position(self):
        self.deletedPositions += 1
        self.activePositions -= 1
        self.save()
        return self.numberOfPositions

    def restore_position(self):
        self.deletedPositions -= 1
        self.activePositions += 1
        return self.numberOfPositions

    def ordered_position_set(self):
        return self.position_set.order_by("orderNumberInOffer")

    def __str__(self):
        return f"Klient: {self.customer.customer_name}, kontakt: {self.customerContact.name}, adres: {self.customerAddress.address}"

    STATUS = ((1, "Nowa"),)
    signature = models.CharField(max_length=64, null=False)
    createdBy = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="createdBy"
    )
    comments = models.TextField(verbose_name="Komentarz")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    lastModified = models.DateTimeField(
        auto_now=True, verbose_name="Data ostaniej edycji"
    )
    status = models.IntegerField(choices=STATUS, default=1, verbose_name="Status")
    expirationDate = models.DateField(
        null=False, default=now_plus_month, verbose_name="Data wygaśnięcia"
    )
    customerContact = models.ForeignKey(Contact, null=True, on_delete=models.SET_NULL)
    customerAddress = models.ForeignKey(Address, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, null=False, on_delete=models.PROTECT)
    numberOfPositions = models.IntegerField(
        null=True, default=0, verbose_name="Ilość pozycji"
    )
    activePositions = models.PositiveIntegerField(default=1, null=False)
    deletedPositions = models.PositiveIntegerField(default=0, null=False)
    calculationUser = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="calculationUser"
    )


class Position(models.Model):

    def get_product_count(self, deleted=False):
        return Position.objects.filter(position=self).filter(deleted=deleted).count()

    def get_primary_product(self):
        return Product.objects.filter(position=self).filter(primary=True).first()

    def add_product(self):
        if self.numberOfProducts is None:
            self.numberOfProducts = 1
        else:
            self.numberOfProducts += 1
            self.activeProducts += 1
        self.save()
        print('added')
        return self.numberOfProducts
        

    def remove_product(self):
        self.activeProducts -= 1
        self.deletedProducts += 1
        self.save()
        print('deleted')
        return self.numberOfProducts
        

    def restore_product(self):
        self.activeProducts += 1
        self.deletedProducts -= 1
        self.save()
        print('restored')
        return self.numberOfProducts
        

    def ordered_product_set(self):
        return self.product_set.order_by('-primary',"orderNumberInPosition")

    def delete(self, *args, **kwargs):
        for product in self.product_set.all():
            product.delete()
        self.deleted = True
        self.deletedDate = dateformat.format(timezone.now(), "Y-m-d")
        self.deletedProducts = self.numberOfProducts
        self.save()

    def restore(self):
        for product in self.product_set.all():
            product.restore()
        self.deleted = False
        self.deletedDate = None
        self.save()

    def save(self,commit=True,  *args, **kwargs):
        if self.orderNumberInOffer is None:
            self.orderNumberInOffer = self.offer.numberOfPositions
        super(Position, self).save(*args, **kwargs)

    offer = models.ForeignKey(Offer, null=False, on_delete=models.CASCADE)

    numberOfProducts = models.PositiveIntegerField(
         verbose_name="Ilość produktów", null=True
    )
    activeProducts = models.PositiveIntegerField(default=1, null=False)
    deletedProducts = models.PositiveIntegerField(default=0, null=False)
    orderNumberInOffer = models.IntegerField(null=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    lastModified = models.DateTimeField(
        auto_now=True, verbose_name="Data ostaniej edycji"
    )
    deleted = models.BooleanField(default=False, null=False)
    deletedDate = models.DateTimeField(null=True)


class Product(models.Model):
    class Size(models.IntegerChoices):
        Wewnętrzny = 1
        Zewnętrzny = 2
        Mieszany = 3

    def save(self, *args, **kwargs):
        if self.orderNumberInPosition is None:
            self.orderNumberInPosition = self.position.add_product()
        super(Product, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.deletedDate = dateformat.format(timezone.now(), "Y-m-d")
        self.save()
        self.position.remove_product()
        return True

    def restore(self, *args, **kwargs):
        self.deleted = False
        self.deletedDate = None
        self.save()
        self.position.restore_product()
        return True

    position = models.ForeignKey(Position, null=False, on_delete=models.CASCADE)
    orderNumberInPosition = models.IntegerField(null=False)
    name = models.CharField(max_length=128, null=False, verbose_name="Nazwa produktu")
    innerIndex = models.CharField(
        max_length=128, null=False, blank=True, verbose_name="Indeks wewnętrzny"
    )
    outsideIndex = models.CharField(
        max_length=128, null=False, blank=True, verbose_name="Indeks zewnętrzny"
    )
    primary = models.BooleanField(
        default=False, null=False, verbose_name="Produkt główny"
    )
    form = models.BooleanField(default=False, null=False, verbose_name="Fason")
    laminating = models.BooleanField(
        default=False, null=False, verbose_name="Kaszerowanie"
    )
    solid = models.BooleanField(default=False, null=False, verbose_name="Lita")
    flexoOverprint = models.BooleanField(
        default=False, null=False, verbose_name="Nadruk Flexo"
    )
    offsetOverprint = models.BooleanField(
        default=False, null=False, verbose_name="Nadruk Offset"
    )
    refinement = models.BooleanField(
        default=False, null=False, verbose_name="Uszlachetnianie"
    )
    width = models.PositiveIntegerField(verbose_name="Szerokość", blank=True, null=True)
    height = models.PositiveIntegerField(verbose_name="Wysokość", blank=True, null=True)
    length = models.PositiveIntegerField(verbose_name="Długość", blank=True, null=True)
    sizeType = models.IntegerField(
        choices=Size.choices, blank=False, default=1, verbose_name="Wymiar"
    )
    numberOfElements = models.PositiveIntegerField(
        verbose_name="Pudło z części", blank=True, null=True
    )
    gluedJoin = models.BooleanField(
        default=False, null=False, verbose_name="Łączenie klejone"
    )
    sewnJoin = models.BooleanField(
        default=False, null=False, verbose_name="Łączenie szyte"
    )
    mixedJoin = models.BooleanField(
        default=False, null=False, verbose_name="Łączenie inne"
    )
    commentJoin = models.CharField(max_length=64, blank=True, verbose_name="")
    deliveryVariantOne = models.PositiveIntegerField(
        verbose_name="Wariant 1", blank=True, null=True
    )
    deliveryVariantTwo = models.PositiveIntegerField(
        verbose_name="Wariant 2", blank=True, null=True
    )
    deliveryVariantThree = models.PositiveIntegerField(
        verbose_name="Wariant 3", blank=True, null=True
    )
    deliveryYearly = models.PositiveIntegerField(
        verbose_name="Ilość roczna", blank=True, null=True
    )
    comments = models.TextField(blank=True, verbose_name="Uwagi dodatkowe", null=True)
    contactPerson = models.ForeignKey(
        Contact,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name="Osoba kontaktowa",
    )
    deliveryAddress = models.ForeignKey(
        Address,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        verbose_name="Adres dostawy",
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name="Data utworzenia")
    lastModified = models.DateTimeField(
        auto_now=True, verbose_name="Data ostaniej edycji"
    )
    deleted = models.BooleanField(default=False, null=False, verbose_name="Usunięto?")
    deletedDate = models.DateTimeField(null=True, verbose_name="Data usunięcia")
