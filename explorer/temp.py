import os, sys
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/explorer')
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/library')
os.environ['DJANGO_SETTINGS_MODULE'] = 'explorer.settings'
import django
django.setup()

from blocks.models import BlockRow, Transaction, TxInput, TxOutput 
from library.network import SimpleNode, GetDataMessage, BLOCK_DATA_TYPE, TX_DATA_TYPE, BlockMessage
from library.block import Block
from library.tx import Tx, TxIn, TxOut
from library.helper import bit_field_to_bytes
from helper_functions import get_type

temp = b'<J\xca#\xe3B\x17\x94\xf5\xf3\x8f\n>9[\xe7\xfb{\xb5\xf5\xc55\x8a\xe0}W\x92\xfa\xcd\xa6\x91Q'
print(temp.hex())

bitfield = [0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print('bytes', bit_field_to_bytes(bitfield))
