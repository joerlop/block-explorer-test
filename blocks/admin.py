from django.contrib import admin

# Register your models here.

from .models import BlockRow, Transaction, TxInput, TxOutput

admin.site.register(BlockRow)
admin.site.register(Transaction)
admin.site.register(TxInput)
admin.site.register(TxOutput)