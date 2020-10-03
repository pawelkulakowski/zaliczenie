from django import forms
from opakowania import models


class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['name', 'tax_code', 'description']


class AddressForm(forms.ModelForm):
    class Meta:

        model = models.Address
        fields = ['zip_code', 'city', 'address', 'primary']


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.Contact

        fields = ['name', 'phone', 'email', 'position', 'primary']