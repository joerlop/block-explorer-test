from django.db import models

# Create your models here.

class BlockRow(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    hash_id = models.CharField(max_length=200, unique=True)
    version = models.BigIntegerField()
    prev_block = models.CharField(max_length=200)
    merkle_root = models.CharField(max_length=200)
    timestamp = models.BigIntegerField()
    bits = models.CharField(max_length=200)
    nonce = models.CharField(max_length=200)
    txn_count = models.BigIntegerField()


class Transaction(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    block = models.ForeignKey(BlockRow, on_delete=models.CASCADE)
    hash_id = models.CharField(max_length=200)
    version = models.BigIntegerField()
    locktime = models.BigIntegerField()
    segwit = models.BooleanField()

class TxInput(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    prev_tx = models.CharField(max_length=200)
    prev_index = models.BigIntegerField()
    script_sig = models.CharField(max_length=200)
    sequence = models.BigIntegerField()
    witness = models.CharField(max_length=200, default=None, blank=True, null=True)

class TxOutput(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    output_type = models.CharField(max_length=200)
    amount = models.BigIntegerField()
    address = models.CharField(max_length=200, default=None, blank=True, null=True)
    script_pubkey = models.CharField(max_length=200)
    op_return_data = models.CharField(max_length=200, default=None, blank=True, null=True)