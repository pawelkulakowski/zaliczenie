from django.shortcuts import render, get_object_or_404, redirect, reverse
from django import views
from opakowania import forms
from opakowania import models
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from datetime import datetime


class MainPageView(views.View):
    def get(self, request):
        return render(request, "opakowania/index.html")


class CustomerAddView(views.View):
    def get(self, request):
        customer_form = forms.CustomerNewForm(prefix="customer")
        address_form = forms.AddressNewForm(initial={"primary": True}, prefix="address")
        contact_form = forms.ContactNewForm(initial={"primary": True}, prefix="contact")

        ctx = {
            "customer_form": customer_form,
            "address_form": address_form,
            "contact_form": contact_form,
        }

        return render(request, "opakowania/customer_add.html", ctx)

    def post(self, request):
        customer_form = forms.CustomerNewForm(request.POST, prefix="customer")
        address_form = forms.AddressNewForm(request.POST, prefix="address")
        contact_form = forms.ContactNewForm(request.POST, prefix="contact")

        ctx = {
            "customer_form": customer_form,
            "address_form": address_form,
            "contact_form": contact_form,
        }

        if (
            customer_form.is_valid()
            and address_form.is_valid()
            and contact_form.is_valid()
        ):
            customer = customer_form.save()
            contact_form.save(customer)
            address_form.save(customer)

            return HttpResponse("dodano")
        else:
            return render(request, "opakowania/customer_add.html", ctx)


class CustomerEditView(views.View):
    def get(self, request, customer_id):
        customer = get_object_or_404(models.Customer, pk=customer_id)
        customer_form = forms.CustomerNewForm(prefix="customer", instance=customer)

        addresses = models.Address.objects.filter(customer_id=customer_id).order_by(
            "-primary"
        )

        contacts = models.Contact.objects.filter(customer_id=customer_id).order_by(
            "-primary"
        )

        ctx = {
            "customer_form": customer_form,
            "addresses": addresses,
            "contacts": contacts,
        }
        return render(request, "opakowania/customer_edit.html", ctx)

    def post(self, request, customer_id):
        customer = get_object_or_404(models.Customer, pk=customer_id)
        addresses = models.Address.objects.filter(customer_id=customer_id).order_by(
            "-primary"
        )
        contacts = models.Contact.objects.filter(customer_id=customer_id).order_by(
            "-primary"
        )
        customer_form = forms.CustomerNewForm(
            request.POST, prefix="customer", instance=customer
        )
        ctx = {
            "customer_form": customer_form,
            "addresses": addresses,
            "contacts": contacts,
        }
        if customer_form.is_valid():
            customer_form.save()
            messages.add_message(request, messages.SUCCESS, "Zmiany pomyślnie zapisane")

        return render(request, "opakowania/customer_edit.html", ctx)


class CustomerSearchView(views.View):
    def get(self, request):
        search_form = forms.CustomerSearchForm()
        customers = models.Customer.objects.all()
        ctx = {"form": search_form, "customers": customers}
        return render(request, "opakowania/customer_search.html", ctx)

    def post(self, request):
        search_form = forms.CustomerSearchForm(request.POST)
        ctx = {"form": search_form}

        if search_form.is_valid():
            name = search_form.cleaned_data["customer_name"]
            tax_code = search_form.cleaned_data["tax_code"]
            customers = models.Customer.objects.filter(
                Q(customer_name__icontains=name) & Q(tax_code__icontains=tax_code)
            )
            ctx.update({"customers": customers})

        return render(request, "opakowania/customer_search.html", ctx)


class ContactSetPrimaryView(views.View):
    def get(self, request, customer_id, contact_id):
        contact = models.Contact.objects.get(pk=contact_id)
        customer = contact.customer
        customer.contact_set.filter(primary=True).update(primary=False)
        contact.primary = True
        contact.save()
        messages.add_message(
            request, messages.SUCCESS, "Pomyślnie ustawiono nowy kontakt główny"
        )
        return redirect(request.META.get("HTTP_REFERER"))


class ContactAddModalView(views.View):
    def get(self, request, customer_id):
        contact_form = forms.ContactNewForm()
        ctx = {"contact_form": contact_form, "customer_id": customer_id}
        return render(request, "opakowania/contact_add_modal.html", ctx)

    def post(self, request, customer_id):
        contact_form = forms.ContactNewForm(request.POST)
        ctx = {"contact_form": contact_form, "customer_id": customer_id}
        if contact_form.is_valid():
            customer = models.Customer.objects.get(pk=customer_id)
            contact_form.save(customer)
        else:
            return render(request, "opakowania/contact_add_modal.html", ctx, status=400)

        messages.add_message(
            request, messages.SUCCESS, "Kontakt pomyślnie dodany do bazy"
        )

        return HttpResponse("")


class ContactEditModalView(views.View):
    def get(self, request, customer_id, contact_id):
        contact = models.Contact.objects.get(pk=contact_id)
        contact_form = forms.ContactNewForm(instance=contact)
        ctx = {
            "contact_form": contact_form,
            "customer_id": customer_id,
            "contact_id": contact_id,
        }
        return render(request, "opakowania/contact_edit_modal.html", ctx)

    def post(self, request, customer_id, contact_id):
        contact = models.Contact.objects.get(pk=contact_id)
        contact_form = forms.ContactNewForm(request.POST, instance=contact)
        ctx = {
            "contact_form": contact_form,
            "customer_id": customer_id,
            "contact_id": contact_id,
        }
        if contact_form.is_valid():
            customer = models.Customer.objects.get(pk=customer_id)
            contact_form.save(customer)
        else:
            return render(
                request, "opakowania/contact_edit_modal.html", ctx, status=400
            )

        messages.add_message(request, messages.SUCCESS, "Zmiany pomyślnie zapisane")

        return HttpResponse("")


class ContactDeleteModalView(views.View):
    def get(self, request, customer_id, contact_id):
        contact = models.Contact.objects.get(pk=contact_id)
        contact_form = forms.ContactNewForm(instance=contact)
        ctx = {
            "contact_form": contact_form,
            "customer_id": customer_id,
            "contact_id": contact_id,
        }
        return render(request, "opakowania/contact_delete_modal.html", ctx)

    def post(self, request, customer_id, contact_id):
        contact = models.Contact.objects.get(pk=contact_id)
        contact.delete()

        messages.add_message(
            request, messages.SUCCESS, "Kontakt pomyślnie kontakt z bazy"
        )

        return HttpResponse("")


class AddressAddModalView(views.View):
    def get(self, request, customer_id):
        address_form = forms.AddressNewForm()
        ctx = {"address_form": address_form, "customer_id": customer_id}
        return render(request, "opakowania/address_add_modal.html", ctx)

    def post(self, request, customer_id):
        address_form = forms.AddressNewForm(request.POST)
        ctx = {"address_form": address_form, "customer_id": customer_id}
        if address_form.is_valid():
            customer = models.Customer.objects.get(pk=customer_id)
            address_form.save(customer)
        else:
            return render(request, "opakowania/address_add_modal.html", ctx, status=400)

        messages.add_message(
            request, messages.SUCCESS, "Adres pomyślnie dodany do bazy"
        )

        return HttpResponse("")


class AddressEditModalView(views.View):
    def get(self, request, customer_id, address_id):
        address = models.Address.objects.get(pk=address_id)
        address_form = forms.AddressNewForm(instance=address)
        ctx = {
            "address_form": address_form,
            "customer_id": customer_id,
            "address_id": address_id,
        }
        print(address.city)
        return render(request, "opakowania/address_edit_modal.html", ctx)

    def post(self, request, customer_id, address_id):
        address = models.Address.objects.get(pk=address_id)
        address_form = forms.AddressNewForm(request.POST, instance=address)
        ctx = {
            "address_form": address_form,
            "customer_id": customer_id,
            "address_id": address_id,
        }
        if address_form.is_valid():
            customer = models.Customer.objects.get(pk=customer_id)
            address_form.save(customer)
        else:
            return render(
                request, "opakowania/address_edit_modal.html", ctx, status=400
            )

        messages.add_message(request, messages.SUCCESS, "Zmiany pomyślnie zapisane")

        return HttpResponse("")


class AddressSetPrimaryView(views.View):
    def get(self, request, customer_id, address_id):
        address = models.Address.objects.get(pk=address_id)
        customer = address.customer
        customer.address_set.filter(primary=True).update(primary=False)
        address.primary = True
        address.save()
        messages.add_message(
            request, messages.SUCCESS, "Pomyślnie ustawiono nowy adres główny"
        )
        return redirect(request.META.get("HTTP_REFERER"))


class AddressDeleteModalView(views.View):
    def get(self, request, customer_id, address_id):
        address = models.Address.objects.get(pk=address_id)
        address_form = forms.AddressNewForm(instance=address)
        ctx = {
            "address_form": address_form,
            "customer_id": customer_id,
            "address_id": address_id,
        }
        return render(request, "opakowania/address_delete_modal.html", ctx)

    def post(self, request, customer_id, address_id):
        address = models.Address.objects.get(pk=address_id)
        address.delete()

        messages.add_message(
            request, messages.SUCCESS, "Adres pomyślnie usunięto z bazy"
        )

        return HttpResponse("")


class OfferNewView(views.View):
    def get(self, request, **kwargs):
        customer = models.Customer.objects.get(pk=self.kwargs['customer_id'])

        if "contact_id" in self.kwargs:
            print(f'kwargs contact_id: {self.kwargs["contact_id"]}')
            contact = models.Contact.objects.get(pk=self.kwargs["contact_id"])
        else:
            contact = (
                models.Contact.objects.filter(customer=customer)
                .filter(primary=True)
                .first()
            )

        if "address_id" in self.kwargs:
            print(f'kwargs address_id: {self.kwargs["address_id"]}')
            address = models.Address.objects.get(pk=self.kwargs["address_id"])
        else:
            address = (
                models.Address.objects.filter(customer=customer)
                .filter(primary=True)
                .first()
            )
        year = datetime.now().year
        month = datetime.now().month
        offer_count = (
            models.Offer.objects.filter(created__year=year)
            .filter(created__month=month)
            .count()
        )
        offer = models.Offer()
        offer.customerAddress = address
        offer.customerContact = contact
        offer.signature = f"{year}/{month}/{offer_count + 1}"
        ctx = {
            "offer": offer,
            "contact": contact,
            "address": address,
            "customer": customer,
        }

        return render(request, "opakowania/offer_add.html", ctx)


class OfferChangeContact(views.View):
    def get(self, request, **kwargs):
        form = forms.ContactChangeForm(
            models.Customer.objects.get(pk=self.kwargs['customer_id']),
        )
        ctx = {"contact_select_form": form, **kwargs}
        return render(request, "opakowania/select_field.html", ctx)

    def post(self, request, **kwargs):
        contact_id = int(request.POST["contactList"])
        return HttpResponseRedirect(
            reverse(
                "add-offer",
                kwargs={"customer_id": self.kwargs['customer_id'], "contact_id": contact_id, 'address_id': self.kwargs['address_id']},
            )
        )


class OfferChangeAddress(views.View):
    def get(self, request, **kwargs):
        form = forms.AddressChangeForm(
            models.Customer.objects.get(pk=self.kwargs['customer_id']),
        )
        ctx = {"address_select_form": form, **kwargs}
        print(kwargs)
        return render(request, "opakowania/select_field.html", ctx)

    def post(self, request, **kwargs):
        address_id = int(request.POST["addressList"])

        return HttpResponseRedirect(
            reverse(
                "add-offer",
                kwargs={"customer_id": self.kwargs['customer_id'],"contact_id": self.kwargs['contact_id'], "address_id": address_id},
            )
        )
