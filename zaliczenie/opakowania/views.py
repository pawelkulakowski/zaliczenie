from django.shortcuts import render
from django.views import View
from opakowania.models import *


class MakeCustomers(View):
    @staticmethod
    def get(request):
        c1 = Customer.objects.create(name="Kliencik", tax_code="111-111-11-11")
        c2 = Customer.objects.create(name="Pudłomat", tax_code="111-111-11-11")
        return render(request, "index.html")