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
    path("", views.MainPageView.as_view(), name="main-page"),
    path("add-customer", views.CustomerAddView.as_view(), name="customer-add"),
    path("search-customer", views.CustomerSearchView.as_view(), name="customer-search"),
    path(
        "customer/<int:customer_id>/",
        views.CustomerEditView.as_view(),
        name="customer-edit",
    ),
    path(
        "customer/<int:customer_id>/contact_primary/<int:contact_id>",
        views.ContactSetPrimaryView.as_view(),
        name="contact-set-primary",
    ),
    path(
        "customer/<int:customer_id>/add-contact",
        views.ContactAddModalView.as_view(),
        name="customer-add-contact",
    ),
    path(
        "customer/<int:customer_id>/edit-contact/<int:contact_id>/",
        views.ContactEditModalView.as_view(),
        name="customer-edit-contact",
    ),
    path(
        "customer/<int:customer_id>/delete-contact/<int:contact_id>/",
        views.ContactDeleteModalView.as_view(),
        name="customer-delete-contact",
    ),
    path(
        "customer/<int:customer_id>/add-address",
        views.AddressAddModalView.as_view(),
        name="customer-add-address",
    ),
    path(
        "customer/<int:customer_id>/address_primary/<int:address_id>",
        views.AddressSetPrimaryView.as_view(),
        name="address-set-primary",
    ),
    path(
        "customer/<int:customer_id>/edit-address/<int:address_id>/",
        views.AddressEditModalView.as_view(),
        name="customer-edit-address",
    ),
    path(
        "customer/<int:customer_id>/delete-address/<int:address_id>/",
        views.AddressDeleteModalView.as_view(),
        name="customer-delete-address",
    ),
    re_path(
        r"^customer/(?P<customer_id>\d+)/add-offer/(?P<contact_id>\d+)/(?P<address_id>\d+)/$",
        views.OfferNewView.as_view(),
        name="add-offer",
    ),
    path(
        "customer/<int:customer_id>/add-offer/<int:contact_id>/<int:address_id>/change-contact",
        views.OfferChangeContact.as_view(),
        name="offer-change-contact",
    ),
    path(
        "customer/<int:customer_id>/add-offer/<int:contact_id>/<int:address_id>/change-address",
        views.OfferChangeAddress.as_view(),
        name="offer-change-address",
    ),
    path(
        "customer/<int:customer_id>/edit-offer/<int:offer_id>",
        views.OfferEditView.as_view(),
        name="offer-edit",
    ),
    path(
        "customer/<int:customer_id>/edit-offer/<int:offer_id>/add-product",
        views.AddProductView.as_view(),
        name="product-add",
    ),
    path(
        "customer/<int:customer_id>/edit-offer/<int:offer_id>/add-product/<int:position_id>",
        views.AddProductView.as_view(),
        name="product-add",
    ),
    path(
        "customer/<int:customer_id>/edit-offer/<int:offer_id>/delete-position/<int:position_id>",
        views.PositionDeleteModalView.as_view(),
        name="position-delete",
    ),
    path(
        "delete-product/<int:product_id>",
        views.ProductDeleteModalView.as_view(),
        name="product-delete",
    ),
    path(
        "restore-product/<int:product_id>",
        views.ProductRestoreView.as_view(),
        name="product-restore",
    ),
    re_path(
        r"^customer/(?P<customer_id>\d+)/offers/",
        views.CustomerDetail.as_view(),
        name="customer-offers",
    ),
]
