"""zaliczenie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from opakowania import views

urlpatterns = [
    path('', views.MainPageView.as_view(), name='main-page'),
    path('add-customer', views.CustomerAddView.as_view(), name='customer-add'),
    path('search-customer', views.CustomerSearchView.as_view(), name='customer-search'),
    path('customer/<int:customer_id>/', views.CustomerEditView.as_view(), name='customer-edit'),
    path('customer/<int:customer_id>/<int:contact_id>', views.ContactSetPrimaryView.as_view(), name='contact-set-primary'),
    path('customer/<int:customer_id>/add-contact', views.ContactAddModalView.as_view(), name='customer-add-contact'),
    path('customer/<int:customer_id>/edit-contact/<int:contact_id>/', views.ContactEditModalView.as_view(), name='customer-edit-contact'),
    path('customer/<int:customer_id>/add-address', views.AddressAddModalView.as_view(), name='customer-add-address'),
    path('customer/<int:customer_id>/edit-address/<int:address_id>/', views.AddressEditModalView.as_view(), name='customer-edit-address'),
]
