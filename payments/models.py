import uuid

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class AccessToken(models.Model):
    token = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Transaction(models.Model):
    """This model records all the mpesa payment transactions"""

    class Status(models.TextChoices):
        PENDING = "PENDING"
        FAILED = "FAILED"
        SUCCESS = "SUCCESS"

    transaction_no = models.CharField(default=uuid.uuid4, max_length=50, unique=True)
    phone_number = PhoneNumberField(null=False, blank=False)
    checkout_request_id = models.CharField(max_length=200)
    # account_reference = models.CharField(max_length=40, blank=True)
    # transaction_description = models.TextField(null=True, blank=True)
    amount = models.CharField(max_length=10)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    receipt_no = models.CharField(max_length=200, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=200, blank=True, null=True)
