"""Payments urls"""
from django.urls import path

from .views import mpesa_checkout, mpesa_callback

urlpatterns = [
    path("pay/", mpesa_checkout, name="mpesa-payment"),
    path("callback/", mpesa_callback, name="callback"),
]
