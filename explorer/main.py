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

# Connect to node
node = SimpleNode('85.204.96.207')
node.handshake()
# Get all the blocks, starting from the genesis block.
"""
Fill
"""
# For each block header, ask for the block's information.
getdata = GetDataMessage()
getdata.add_data(BLOCK_DATA_TYPE, bytes.fromhex('0000000000000000000995e3397b662e673e275ac904adef1e4e2cfa142a8177'))
node.send(getdata)
received_block = node.wait_for(BlockMessage)
# Save the blocks to the db
new_block = Block(received_block.version, received_block.prev_block, received_block.merkle_root, received_block.timestamp, received_block.bits, received_block.nonce)
new_row = BlockRow(hash_id=new_block.hash().hex(), version=received_block.version, prev_block=received_block.prev_block, merkle_root=received_block.merkle_root, timestamp=received_block.timestamp, bits=received_block.bits, nonce=received_block.nonce, txn_count=received_block.txn_count)
new_row.save()
# Save each of the block's txs to the db.
for txn in received_block.txns:
    new_tx_row = Transaction(block=new_row, hash_id=txn.id(), version=txn.version, locktime=txn.locktime, segwit=txn.segwit)
    new_tx_row.save()
    for tx_in in txn.tx_inputs:
        new_tx_input_row = TxInput(transaction=new_tx_row, prev_tx=tx_in.prev_tx, prev_index=tx_in.prev_index)
        new_tx_input_row.save()
    for tx_out in txn.tx_outputs:
        new_tx_output_row = TxOutput(transaction=new_tx_row, amount=tx_out.amount, address=tx_out.script_pubkey.address())
        new_tx_output_row.save()

# new_block = Block(received_block.version, received_block.prev_block, received_block.merkle_root, received_block.timestamp, received_block.bits, received_block.nonce)
# print(new_block.hash().hex())

prev = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11\xe2\xe1(yw\xe1M\xa1\x8e\x94\x00q\xab\xe7\xa6\xcasfw\x96fz'
print(prev.hex())