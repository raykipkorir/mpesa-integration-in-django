from django import forms
from .models import Transaction


class MpesaCheckoutForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["phone_number", "amount"]
