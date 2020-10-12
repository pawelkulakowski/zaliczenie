from django.shortcuts import render, get_object_or_404, redirect
from django import views
from opakowania import forms
from opakowania import models
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages


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
        results = models.Customer.objects.all()
        ctx = {"form": search_form, "results": results}
        return render(request, "opakowania/customer_search.html", ctx)

    def post(self, request):
        search_form = forms.CustomerSearchForm(request.POST)
        ctx = {"form": search_form}

        if search_form.is_valid():
            name = search_form.cleaned_data["customer_name"]
            tax_code = search_form.cleaned_data["tax_code"]
            results = models.Customer.objects.filter(
                Q(customer_name__icontains=name) & Q(tax_code__icontains=tax_code)
            )
            ctx.update({"results": results})

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
            return render(request, "opakowania/address_edit_modal.html", ctx, status=400)

        messages.add_message(
            request, messages.SUCCESS, "Zmiany pomyślnie zapisane"
        )

        return HttpResponse("")