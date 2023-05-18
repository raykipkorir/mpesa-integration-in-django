import logging
import re

import requests
from django.conf import settings
from django.utils import timezone

from payments.models import AccessToken

from .exceptions import MpesaError
from payments.models import Transaction

def generate_access_token():
    """Generate access token"""
    res = requests.get(
        settings.ACCESS_TOKEN_URL,
        auth=(settings.CONSUMER_KEY, settings.CONSUMER_SECRET),
        params={"grant_type": "client_credentials"},
        timeout=30
    )
    if res.status_code == 200:
        access_token = res.json()["access_token"]
        AccessToken.objects.all().delete()
        access_token = AccessToken.objects.create(token=access_token)
        return access_token
    else:
        raise MpesaError("Unable to generate access token")

def get_access_token():
    access_token = AccessToken.objects.first()
    if access_token is None:
        access_token =  generate_access_token()
    else:
        delta = timezone.now() - access_token.created_at
        minutes = (delta.total_seconds()//60)
        if minutes > 50:
            # Access token expired
            access_token = generate_access_token()

    return access_token.token

def validate_phone_number(phone_number: str):
    pattern = r"^(?:254|\+254|0)?((?:(?:7(?:(?:[01249][0-9])|(?:5[789])|(?:6[89])))|(?:1(?:[1][0-5])))[0-9]{6})$"
    if re.match(pattern, phone_number):
        return phone_number
    else: 
        return None

def format_phone_number(phone_number: str):
    if phone_number.startswith("+"):
        return phone_number.strip("+")
    # elif phone_number.startswith("0"):
    #     return phone_number.replace("0", "254", 1)
    # else:
    #     return phone_number


def get_status(data):
    # if status is 0 means payment was successful otherwise payment is unsuccessful
    try:
        status = data["Body"]["stkCallback"]["ResultCode"]
    except Exception as e:
        logging.error(f"Error: {e}")
        status = 1 
    return status

def get_transaction_object(data):
    checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
    transaction= Transaction.objects.get(checkout_request_id=checkout_request_id)
    return transaction

def handle_successful_pay(data, transaction):
    items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
    for item in items:
        if item["Name"] == "Amount":
            amount = item["Value"]
        elif item["Name"] == "MpesaReceiptNumber":
            receipt_no = item["Value"]
        elif item["Name"] == "PhoneNumber":
            phone_number = item["Value"]

    # transaction.amount = amount
    # transaction.phone_number = PhoneNumber(raw_input=phone_number)
    transaction.receipt_no = receipt_no
    transaction.status = Transaction.Status.SUCCESS

    return transaction

def callback_handler(data):
    status = get_status(data)
    transaction = get_transaction_object(data)
    if status==0:
        transaction = handle_successful_pay(data, transaction)
    else:
        transaction.status = Transaction.Status.FAILED

    transaction.save()
    return
