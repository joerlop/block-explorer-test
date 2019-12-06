import os, sys
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/explorer')
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/library')
os.environ['DJANGO_SETTINGS_MODULE'] = 'explorer.settings'
import django
django.setup()

from blocks.models import BlockRow, Transaction, TxInput, TxOutput 
from library.network import SimpleNode, GetDataMessage, BLOCK_DATA_TYPE, BlockMessage
from library.block import Block
from library.tx import Tx, TxIn, TxOut


# Returns the type of a given tx output.
def get_type(tx_output):
    if tx_output.script_pubkey.is_p2pk_script_pubkey():
        return 'P2PK'
    elif tx_output.script_pubkey.is_p2pkh_script_pubkey():
        return 'P2PKH'
    elif tx_output.script_pubkey.is_p2sh_script_pubkey():
        return 'P2SH'
    elif tx_output.script_pubkey.is_p2wpkh_script_pubkey():
        return 'P2WPKH'
    elif tx_output.script_pubkey.is_p2wsh_script_pubkey():
        return 'P2WSH'
    elif tx_output.script_pubkey.is_op_return_pubkey():
        return 'OP_RETURN'
    return None
