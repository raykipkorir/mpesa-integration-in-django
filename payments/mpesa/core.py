import base64
from datetime import datetime

import requests
from django.conf import settings
from requests import Response

from .utils import get_access_token


class MpesaGateway:
    """Mpesa gateway"""

    def __init__(self) -> None:
        self.password = None
        self.timestamp = None


    def stk_push(self, phone_number: str, amount: int) -> Response:
        """Stk push"""
        self.password = self.generate_password()
        payload = {
            "BusinessShortCode": settings.BUSINESS_SHORTCODE,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.CALLBACK_URL,
            "AccountReference": "TEST",
            "TransactionDesc": "Transaction description"
        }
        headers = {
			'Authorization': 'Bearer ' + get_access_token()
		}
        
        response = requests.post(settings.STK_PUSH_URL, json=payload, headers=headers, timeout=30)    
        return response
        
    def generate_password(self) -> str:
        """Generates mpesa api password using the provided shortcode and passkey"""
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_str = settings.BUSINESS_SHORTCODE + settings.PASS_KEY + self.timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8")
    