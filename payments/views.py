"""Payments views"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from payments.mpesa.core import MpesaGateway
from payments.mpesa.utils import callback_handler, format_phone_number

from .forms import MpesaCheckoutForm
from .models import Transaction


def mpesa_checkout(request):
    """Initiate stk push prompt"""
    form = MpesaCheckoutForm()
    if request.method == "POST":

        mpesa_gateway = MpesaGateway()

        form = MpesaCheckoutForm(request.POST)

        if form.is_valid():
            phone_number = request.POST.get("phone_number")
            formatted_phonenumber = format_phone_number(phone_number)
            amount = form.cleaned_data.get("amount")
            response = mpesa_gateway.stk_push(phone_number=formatted_phonenumber, amount=amount)
            json_response = response.json()
            if response.ok:
                instance: Transaction = form.save(commit=False)
                instance.checkout_request_id = json_response.get("CheckoutRequestID")
                instance.ip = request.META.get("REMOTE_ADDR")
                instance.save()

            return JsonResponse(json_response, safe=False) 

    return render(request, "payments/mpesa.html", {"form": form})


@csrf_exempt
def mpesa_callback(request):
    message = 'MPESA Express payment result'

    if request.method == "POST":
        data = request.body.decode().replace('\n', ' ')
        callback_handler(data)
    return HttpResponse(message)
