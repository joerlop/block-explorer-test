from django.db import models

# Create your models here.

class BlockRow(models.Model):
    hash_id = models.CharField(max_length=100)
    version = models.IntegerField()
    prev_block = models.BinaryField(editable=True)
    merkle_root = models.BinaryField(editable=True)
    timestamp = models.IntegerField()
    bits = models.BinaryField(editable=True)
    nonce = models.BinaryField(editable=True)
    txn_count = models.IntegerField()


class Transaction(models.Model):
    block = models.ForeignKey(BlockRow, on_delete=models.CASCADE)
    hash_id = models.CharField(max_length=100)
    version = models.IntegerField()
    locktime = models.IntegerField()
    segwit = models.BooleanField()

class TxInput(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    prev_tx = models.BinaryField(editable=True)
    prev_index = models.IntegerField()

class TxOutput(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    amount = models.IntegerField()
    address = models.CharField(max_length=100)
