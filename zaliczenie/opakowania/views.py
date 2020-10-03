from django.shortcuts import render
from django import views
from opakowania import forms


class MainPageView(views.View):
    def get(self, request):
        return render(request, 'opakowania/index.html')


class CustomerAddView(views.View):

    def get(self, request):
        customer_form = forms.CustomerForm()
        address_form = forms.AddressForm()
        contact_form = forms.ContactForm()

        ctx = {
            'customer_form': customer_form,
            'address_form': address_form,
            'contact_form': contact_form,
            'primary': True
        }

        return render(request, 'opakowania/customer_add.html', ctx)
