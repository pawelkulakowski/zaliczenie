from django import forms
from opakowania import models
from opakowania import validators
import re
from django.core.validators import ValidationError, RegexValidator


class CustomerNewForm(forms.ModelForm):
    def clean_tax_code(self):
        tax_code = self.cleaned_data["tax_code"]
        if self.instance:
            qs = models.Customer.objects.exclude(pk=self.instance.id)
        else:
            qs = models.Customer.all()

        if qs.filter(tax_code=tax_code).exists():
            raise ValidationError("Klient z tym numerem NIP już istnieje")
        return tax_code

    def clean_customer_name(self):
        name = self.cleaned_data["customer_name"]
        if str.strip(name) == "":
            raise ValidationError("Nazwa klienta jest obowiązkowa")
        return name

    def clean(self):
        cleaned_data = super(CustomerNewForm, self).clean()
        return cleaned_data

    class Meta:
        model = models.Customer
        fields = ["customer_name", "tax_code", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"spellcheck": "true", "rows": 5})
        }


class CustomerSearchForm(forms.Form):
    alphanumeric = RegexValidator(r"^[0-9]*$", "Dozwolone są tylko cyfry")

    customer_name = forms.CharField(
        label="Fragment nazwy",
        help_text="Podaj fragment wyszukiwanego nazwiska",
        required=False,
    )

    tax_code = forms.CharField(
        max_length="11",
        label="Fragment NIPu",
        help_text='Podaj fragment NIPu bez "-"',
        required=False,
        validators=[alphanumeric],
    )

    def clean_customer_name(self):
        name = self.cleaned_data["customer_name"]
        return str.strip(name)


class AddressNewForm(forms.ModelForm):
    def clean_zip_code(self):
        zip_code = self.cleaned_data["zip_code"]
        if re.search("[0-9][0-9]-[0-9][0-9][0-9]$", zip_code) is None:
            raise ValidationError("Kod pocztowy powinien mieć format XX-XXX")
        return zip_code

    def save(self, customer):
        address = super().save(commit=False)
        address.customer = customer
        if address.primary:
            customer.address_set.filter(primary=True).update(primary=False)
        elif not customer.address_set.filter(primary=True).exists():
            address.primary = True
        return address.save()

    class Meta:
        model = models.Address
        fields = ["zip_code", "city", "address"]


class ContactNewForm(forms.ModelForm):
    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if phone != "" and re.search("^\d{9}$", phone) is None:
            raise ValidationError("Numer telefonu powinien mieć format XXXXXXXXX")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        if phone == "" and email == "":
            raise ValidationError(
                "Podaj chociaż jeden sposób kontaku (telefon lub email)"
            )
        return self.cleaned_data

    def save(self, customer):
        contact = super().save(commit=False)
        contact.customer = customer
        if contact.primary:
            customer.contact_set.filter(primary=True).update(primary=False)
        elif not customer.contact_set.filter(primary=True).exists():
            contact.primary = True
        return contact.save()

    class Meta:
        model = models.Contact
        fields = ["name", "phone", "email", "position"]


class OfferNewForm(forms.ModelForm):
    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["addressList"].queryset = models.Address.objects.filter(
            customer_pk=self.instance.id
        )

    address_list = models.AddressChoiceField(queryset=None)


class ContactChangeForm(forms.Form):
    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contactList"].queryset = models.Contact.objects.filter(
            customer=customer
        ).order_by("-primary")

    contactList = models.ConatactChoiceField(
        queryset=None, label="Wybierz nowy kontakt z listy", initial=1
    )


class AddressChangeForm(forms.Form):
    def __init__(self, customer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["addressList"].queryset = models.Address.objects.filter(
            customer=customer
        ).order_by("-primary")

    addressList = models.AddressChoiceField(
        queryset=None, label="Wybierz nowy adres z listy", initial=1
    )


class OfferCommentForm(forms.Form):
    comments = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "cols": 40, "spellcheck": "true"}),
        required=False,
        label=False,
    )


class AddPositionForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
            }
        ),
        label="Nazwa",
        max_length=128,
    )
    innerIndex = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
            }
        ),
        label="Indeks wewnętrzny",
        required=False,
        max_length=128,
    )
    outsideIndex = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 2,
            }
        ),
        label="Indeks zewnętrzny",
        required=False,
        max_length=128,
    )
    commentJoin = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 2, "placeholder": "Dodatkowe informacje na temat łączenia"}
        ),
        label=False,
        required=False,
    )
    comments = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": "Dodatkowe informacje dotyczące zlecenia"}
        ),
        label="Uwagi dodatkowe",
        required=False,
    )
    deliveryVariantOne = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wariant 1"}),
        label="Dostawa",
        required=True,
        validators=[validators.positive_number_validator],
    )
    deliveryVariantTwo = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wariant 2"}),
        label=False,
        required=False,
        validators=[validators.positive_number_validator],
    )
    deliveryVariantThree = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Wariant 3"}),
        label=False,
        required=False,
        validators=[validators.positive_number_validator],
    )
    deliveryYearly = forms.IntegerField(
        widget=forms.NumberInput(attrs={"placeholder": "Rocznie"}),
        label=False,
        required=False,
        validators=[validators.positive_number_validator],
    )

    class Meta:
        model = models.Product
        fields = [
            "name",
            "primary",
            "form",
            "laminating",
            "solid",
            "flexoOverprint",
            "refinement",
            "width",
            "height",
            "commentJoin",
            "comments",
            "contactPerson",
            "deliveryAddress",
            "deliveryVariantOne",
            "deliveryVariantThree",
            "deliveryVariantTwo",
            "deliveryYearly",
            "gluedJoin",
            "innerIndex",
            "length",
            "mixedJoin",
            "numberOfElements",
            "offsetOverprint",
            "outsideIndex",
            "sewnJoin",
            "sizeType",
        ]

    def __init__(self, offer, *args, **kwargs):
        super(AddPositionForm, self).__init__(*args, **kwargs)
        self.fields["contactPerson"].queryset = offer.customer.contact_set.all()
        self.fields["contactPerson"].empty_label = None
        self.fields["deliveryAddress"].queryset = offer.customer.address_set.all()
        self.fields["deliveryAddress"].empty_label = None

        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control-sm"


class AddProductForm(AddPositionForm):
    def __init__(self, offer, *args, **kwargs):
        super(AddProductForm, self).__init__(offer, *args, **kwargs)

    class Meta:
        model = models.Product
        fields = [
            "name",
            "primary",
            "form",
            "laminating",
            "solid",
            "flexoOverprint",
            "refinement",
            "width",
            "height",
            "commentJoin",
            "comments",
            "contactPerson",
            "deliveryAddress",
            "deliveryVariantOne",
            "deliveryVariantThree",
            "deliveryVariantTwo",
            "deliveryYearly",
            "gluedJoin",
            "innerIndex",
            "length",
            "mixedJoin",
            "numberOfElements",
            "offsetOverprint",
            "outsideIndex",
            "sewnJoin",
            "sizeType",
            "position",
        ]