from django.contrib import admin
from .models import AccessToken, Transaction
# Register your models here.


admin.site.register(AccessToken)
admin.site.register(Transaction)
