from .models import BlockRow
from rest_framework import serializers


class BlockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BlockRow
        fields = ['pk_id', 'hash_id', 'version', 'prev_block', 'merkle_root', 'timestamp', 'bits', 'nonce', 'txn_count']
