import os, sys
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/explorer')
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/library')
os.environ['DJANGO_SETTINGS_MODULE'] = 'explorer.settings'
import django
django.setup()

from blocks.models import BlockRow, Transaction, TxInput, TxOutput 
from library.network import SimpleNode, GetDataMessage, BLOCK_DATA_TYPE, TX_DATA_TYPE, BlockMessage, VersionMessage
from library.block import Block
from library.tx import Tx, TxIn, TxOut
from helper_functions import get_type

# Connect to node
node = SimpleNode('116.58.171.67')
node.handshake()
# Get all the blocks, starting from the genesis block.
"""
Fill
"""
# For each block header, ask for the block's information.
getdata = GetDataMessage()
getdata.add_data(BLOCK_DATA_TYPE, bytes.fromhex('000000000000000000158ceac0cab2451d26df2d0e356549e2f410b15c364466'))
node.send(getdata)
received_block = node.wait_for(BlockMessage)
""" Save the blocks to the db """
# First I create a Block object to be able to get its id.
new_block = Block(received_block.version, received_block.prev_block, received_block.merkle_root, received_block.timestamp, received_block.bits, received_block.nonce)
# Then I create the row object to save in the db.
new_row = BlockRow(hash_id=new_block.hash().hex(), version=received_block.version, prev_block=received_block.prev_block, merkle_root=received_block.merkle_root, timestamp=received_block.timestamp, bits=received_block.bits, nonce=received_block.nonce, txn_count=received_block.txn_count)
new_row.save()
# Save each of the block's txs to the db.
count = 0
for txn in received_block.txns:
    new_tx_row = Transaction(block=new_row, hash_id=txn.id(), version=txn.version, locktime=txn.locktime, segwit=txn.segwit)
    new_tx_row.save()
    for tx_in in txn.tx_inputs:
        # Check if the input has a witness.
        if hasattr(tx_in, 'witness'):
            # This is a list, so we need to serialize it.
            witness_list = tx_in.witness
            # The following code serializes the witness.
            witness = b''
            for item in tx_in.witness:
                if type(item) == int:
                    witness += int_to_little_endian(item, 1)
                else:
                    witness += encode_varint(len(item)) + item
            # We convert it to hex.
            witness = witness.hex()
        # If input has no witness attribute, witness = None.
        else:
            witness = None
        new_tx_input_row = TxInput(transaction=new_tx_row, prev_tx=tx_in.prev_tx.hex(), prev_index=tx_in.prev_index, script_sig=tx_in.script_sig.serialize().hex()[2:], sequence=tx_in.sequence, witness=witness)
        new_tx_input_row.save()
    for tx_out in txn.tx_outputs:
        # We need to establish the type of the output.
        out_type = get_type(tx_out)
        # If output is OP_RETURN, address doesn't apply.
        # Also, we need to find the return data.
        if out_type == 'OP_RETURN':
            address = None
            op_return_data = tx_out.script_pubkey.get_op_return_data()
        else:
            address = tx_out.script_pubkey.address()
            op_return_data = None
        new_tx_output_row = TxOutput(transaction=new_tx_row, output_type=out_type, amount=tx_out.amount, address=address, script_pubkey=tx_out.script_pubkey.serialize().hex()[2:], op_return_data=op_return_data)
        new_tx_output_row.save()

# getdata = GetDataMessage()
# getdata.add_data(TX_DATA_TYPE, bytes.fromhex('e270c049903e4726285b0f0b5aff7aafb3e60b9ba5a1899aae4fd2d2928b7f14'))
# node.send(getdata)
# received_tx = node.wait_for(Tx)
