from django.shortcuts import render, get_object_or_404, redirect, reverse
from django import views
from django.views.generic.edit import FormView, FormMixin, SingleObjectMixin, UpdateView
from django.views.generic.list import ListView
from opakowania import forms
from opakowania import models
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.contrib import messages
from datetime import datetime
import requests


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

            return redirect(reverse("search-customer"))
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

        return redirect(reverse('customer-search'))


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

        if contact_form.is_valid():
            customer = models.Customer.objects.get(pk=customer_id)
            contact_form.cleaned_data["primary"] = contact.primary
            contact_form.save(customer)
        else:
            ctx = {
                "contact_form": contact_form,
                "customer_id": customer_id,
                "contact_id": contact_id,
            }
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

        c

        return HttpResponse("")


class OfferNewView(views.View):
    def get(self, request, **kwargs):
        customer = models.Customer.objects.get(pk=self.kwargs["customer_id"])
        commentForm = forms.OfferCommentForm()

        if "contact_id" in self.kwargs:
            contact = models.Contact.objects.get(pk=self.kwargs["contact_id"])
        else:
            contact = (
                models.Contact.objects.filter(customer=customer)
                .filter(primary=True)
                .first()
            )

        if "address_id" in self.kwargs:
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
            "commentForm": commentForm,
        }

        return render(request, "opakowania/offer_add.html", ctx)

    def post(self, request, **kwargs):
        customer = models.Customer.objects.get(pk=self.kwargs["customer_id"])
        address = models.Address.objects.get(pk=self.kwargs["address_id"])
        contact = models.Contact.objects.get(pk=self.kwargs["contact_id"])
        commentForm = forms.OfferCommentForm(request.POST)
        offer = models.Offer()
        offer.customer = customer
        offer.customerAddress = address
        offer.customerContact = contact
        commentForm.full_clean()
        offer.comments = commentForm.cleaned_data["comments"]
        year = datetime.now().year
        month = datetime.now().month
        offer_count = (
            models.Offer.objects.filter(created__year=year)
            .filter(created__month=month)
            .count()
        )
        offer.signature = f"{year}/{month}/{offer_count + 1}"

        offer.save()
        messages.add_message(
            request, messages.SUCCESS, "Oferta pomyślnie dodana do bazy"
        )
        return redirect(
            reverse(
                "offer-edit",
                kwargs={
                    "customer_id": self.kwargs["customer_id"],
                    "offer_id": offer.id,
                },
            )
        )


class OfferChangeContact(views.View):
    def get(self, request, **kwargs):
        form = forms.ContactChangeForm(
            models.Customer.objects.get(pk=self.kwargs["customer_id"]),
        )
        ctx = {"contact_select_form": form, **kwargs}
        return render(request, "opakowania/select_field.html", ctx)

    def post(self, request, **kwargs):
        contact_id = int(request.POST["contactList"])
        return HttpResponseRedirect(
            reverse(
                "add-offer",
                kwargs={
                    "customer_id": self.kwargs["customer_id"],
                    "contact_id": contact_id,
                    "address_id": self.kwargs["address_id"],
                },
            )
        )


class OfferChangeAddress(views.View):
    def get(self, request, **kwargs):
        form = forms.AddressChangeForm(
            models.Customer.objects.get(pk=self.kwargs["customer_id"]),
        )
        ctx = {"address_select_form": form, **kwargs}
        return render(request, "opakowania/select_field.html", ctx)

    def post(self, request, **kwargs):
        address_id = int(request.POST["addressList"])

        return HttpResponseRedirect(
            reverse(
                "add-offer",
                kwargs={
                    "customer_id": self.kwargs["customer_id"],
                    "contact_id": self.kwargs["contact_id"],
                    "address_id": address_id,
                },
            )
        )


class OfferEditView(SingleObjectMixin, ListView):
    template_name = "opakowania/offer_edit.html"
    pk_url_kwarg = "offer_id"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=models.Offer.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = self.object
        context["positions"] = context.pop("object_list")
        return context

    def get_queryset(self, *args, **kwargs):
        return self.object.ordered_position_set()


class AddProductView(views.View):
    def get(self, request, **kwargs):
        offer = models.Offer.objects.get(pk=self.kwargs["offer_id"])
        customer = offer.customer
        contact = offer.customerContact
        address = offer.customerAddress
        if "position_id" in self.kwargs:
            primary = False
            position = models.Position.objects.get(pk=self.kwargs["position_id"])
            form = forms.AddProductForm(
                offer,
                initial={
                    "primary": primary,
                    "contactPerson": contact,
                    "deliveryAddress": address,
                    "position": position
                },
            )
        else:
            primary = True
            form = forms.AddPositionForm(
                offer,
                initial={
                    "primary": primary,
                    "contactPerson": contact,
                    "deliveryAddress": address
                },
            )

        ctx = {"form": form, "offer": offer}
        return render(request, "opakowania/product_add.html", ctx)

    def post(self, request, **kwargs):
        offer = models.Offer.objects.get(pk=self.kwargs["offer_id"])
        if "position_id" in self.kwargs:
            form = forms.AddProductForm(offer, request.POST)
        else:
            form = forms.AddPositionForm(offer, request.POST)
        
        if form.is_valid():
            if form.cleaned_data["primary"]:
                offer.add_position()
                position = models.Position()
                position.offer = offer
                position.save()
                product = models.Product(**form.cleaned_data)
                product.position = position
                product.save()
            else:
                form.save()
                position = form.cleaned_data['position']
                # position.add_product()

            messages.add_message(
                request, messages.SUCCESS, "Produkt pomyślnie dodany do bazy"
            )

            return redirect(
                reverse(
                    "offer-edit",
                    kwargs={
                        "customer_id": self.kwargs["customer_id"],
                        "offer_id": self.kwargs["offer_id"],
                    },
                )
            )

        else:
            messages.error(request, "Błąd formularza")
            ctx = {"form": form, "offer": offer, "errors": form.errors}
            return render(request, "opakowania/product_add.html", ctx)


class ProductEditView(views.View):
    def get(self, request, **kwargs):
        product = models.Product.objects.get(pk=kwargs["product_id"])
        offer = models.Offer.objects.get(pk=kwargs["offer_id"])
        print(product)
        form = forms.AddPositionForm(offer, instance=product)
        ctx = {"form": form, "offer": offer}
        return render(request, "opakowania/product_edit.html", ctx)

    def post(self, request, *args, **kwargs):
        offer = models.Offer.objects.get(pk=kwargs["offer_id"])
        form = forms.AddPositionForm(offer, request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(
                request, messages.SUCCESS, "Zmiany zapisane pomyślnie"
            )
            return redirect(
                reverse(
                    "offer-edit",
                    kwargs={
                        "customer_id": self.kwargs["customer_id"],
                        "offer_id": self.kwargs["offer_id"],
                    },
                )
            )


class CustomerDetail(SingleObjectMixin, ListView):
    template_name = "opakowania/customer_offers_modal.html"
    pk_url_kwarg = "customer_id"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=models.Customer.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = self.object
        context["offers"] = context.pop("object_list")
        return context

    def get_queryset(self):
        return self.object.ordered_offer_set()


class PositionDeleteModalView(views.View):
    def get(self, request, customer_id, offer_id, position_id):
        position = models.Position.objects.get(pk=position_id)
        ctx = {
            "offer_id": offer_id,
            "customer_id": customer_id,
            "position_id": position_id,
        }
        return render(request, "opakowania/position_delete_modal.html", ctx)

    def post(self, request, customer_id, offer_id, position_id):
        position = models.Position.objects.get(pk=position_id)
        position.delete()
        messages.add_message(request, messages.SUCCESS, "Pozycja pomyślnie usunięto")
        return HttpResponse("")


class ProductDeleteModalView(views.View):
    def get(self, request, product_id):
        ctx = {"product_id": product_id}
        return render(request, "opakowania/product_delete_modal.html", ctx)

    def post(self, request, product_id):
        product = models.Product.objects.get(pk=product_id)
        product.delete()

        messages.add_message(request, messages.SUCCESS, "Produkt pomyślnie usunięto")

        return HttpResponse("")


class ProductRestoreView(views.View):
    def get(self, request, product_id):
        product = models.Product.objects.get(pk=product_id)
        product.restore()
        messages.add_message(request, messages.SUCCESS, "Produkt pomyślnie przywrócony")
        return redirect(request.META.get("HTTP_REFERER"))


class PositionRestoreView(views.View):
    def get(self, request, position_id):
        ctx = {'position_id':position_id}
        return render(request, 'opakowania/position_restore_modal.html', ctx)

    def post(self, request, position_id):
        position = models.Position.objects.get(pk=position_id)
        position.restore()
        messages.add_message(request, messages.SUCCESS, "Pozycja i jej produkty pomyślnie przywrócone")
        return HttpResponse("")
