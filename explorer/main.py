import os, sys
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/explorer')
sys.path.append('/Users/jonathanerlich/Documents/git/block-explorer-test/explorer/library')
os.environ['DJANGO_SETTINGS_MODULE'] = 'explorer.settings'
import django
django.setup()

from blocks.models import BlockRow, Transaction, TxInput, TxOutput 
from library.network import SimpleNode, GetDataMessage, BLOCK_DATA_TYPE, TX_DATA_TYPE, BlockMessage, VersionMessage, MSG_WITNESS_BLOCK, GetHeadersMessage, HeadersMessage
from library.block import Block
from library.tx import Tx, TxIn, TxOut
from library.helper import encode_varint, int_to_little_endian
from helper_functions import get_type

# Connect to node
node = SimpleNode('46.248.170.225')
node.handshake()
# Get all the blocks, starting from the genesis block.
"""
Get all block headers starting from the first one..
"""
while True:
    # If there are no objects in the db, we start asking for headers from the genesis block.
    if len(BlockRow.objects.all()) == 0:
        getheaders = GetHeadersMessage(start_block=bytes.fromhex('000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'))
    # Else we start from the last added block.
    else:
        block_hash = BlockRow.objects.all().order_by("-pk_id")[0].hash_id
        getheaders = GetHeadersMessage(start_block=bytes.fromhex(block_hash))
    node.send(getheaders)
    received_headers = node.wait_for(HeadersMessage)
    print('received headers', received_headers)
    # For each block header, ask for the block's information.
    for block in received_headers.blocks:
        # We check that the received block comes after the previous block in the blockchain.
        if len(BlockRow.objects.all()) > 0:
            if BlockRow.objects.all().order_by('-pk_id')[0].hash_id != block.prev_block.hex():
                raise ValueError('Block is not the next one in the blockchain.')
        if block.check_pow() is False:
            raise ValueError('Bad PoW for current block.')
        block = block.hash()
        getdata = GetDataMessage()
        getdata.add_data(MSG_WITNESS_BLOCK, block)
        node.send(getdata)
        received_block = node.wait_for(BlockMessage)
        """ Save the blocks to the db """
        # First I create a Block object to be able to get its id.
        new_block = Block(received_block.version, received_block.prev_block, received_block.merkle_root, received_block.timestamp, received_block.bits, received_block.nonce)
        # Then I create the row object to save in the db.
        new_row = BlockRow(hash_id=new_block.hash().hex(), version=received_block.version, prev_block=received_block.prev_block.hex(), merkle_root=received_block.merkle_root.hex(), timestamp=received_block.timestamp, bits=received_block.bits[::-1].hex(), nonce=received_block.nonce[::-1].hex(), txn_count=received_block.txn_count)
        new_row.save()
        # Save each of the block's txs to the db.
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
                            serialized_item = int_to_little_endian(item, 1)
                            # We check that the item is not empty.
                            if serialized_item != b'\x00':
                                witness += serialized_item
                        else:
                            witness += encode_varint(len(item)) + item
                    # We convert it to hex.
                    witness = witness.hex()[2:]
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