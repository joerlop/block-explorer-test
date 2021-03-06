import socket
import time

from io import BytesIO
from random import randint
from unittest import TestCase

from .block import Block
from .tx import Tx
from .helper import (
    hash256,
    encode_varint,
    int_to_little_endian,
    little_endian_to_int,
    read_varint,
    bytes_to_bit_field
)

TX_DATA_TYPE = 1
BLOCK_DATA_TYPE = 2
FILTERED_BLOCK_DATA_TYPE = 3
COMPACT_BLOCK_DATA_TYPE = 4
MSG_WITNESS_BLOCK = 0x40000002

NETWORK_MAGIC = b'\xf9\xbe\xb4\xd9'
TESTNET_NETWORK_MAGIC = b'\x0b\x11\x09\x07'


class NetworkEnvelope:

    def __init__(self, command, payload, testnet=False):
        # command is an ASCII string identifying the packet content
        self.command = command
        self.payload = payload
        if testnet:
            self.magic = TESTNET_NETWORK_MAGIC
        else:
            self.magic = NETWORK_MAGIC

    def __repr__(self):
        return '{}: {}'.format(self.command.decode('ascii'), self.payload.hex())

    # receives a stream of bytes representing a NetworkEnvelope and returns an object of the class.
    @classmethod
    def parse(cls, stream, testnet=False):
        # first 4 bytes are the magic.
        magic = stream.read(4)
        # check that we received a magic.
        if magic == b'':
            raise IOError('Connection reset!')
        # check that magic is correct.
        if testnet:
            expected_magic = TESTNET_NETWORK_MAGIC
        else:
            expected_magic = NETWORK_MAGIC
        if expected_magic != magic:
            raise SyntaxError(
                f"Magic is not right: {magic.hex()} vs. {expected_magic.hex()}")
        # next 12 are the command.
        command = stream.read(12)
        # strip command from leading zeros.
        command = command.strip(b'\x00')
        # next 4 are the payload length, in LE.
        payload_length = little_endian_to_int(stream.read(4))
        # next 4 are the payload checksum.
        payload_checksum = stream.read(4)
        # next is the payload.
        payload = stream.read(payload_length)
        # check checksum is correct.
        calculated_checksum = hash256(payload)[:4]
        if payload_checksum != calculated_checksum:
            raise IOError('checksum does not match')
        return cls(command, payload, testnet)

    # returns the bytes serialization of this NetworkEnvelope object - page 179.
    def serialize(self):
        magic = self.magic
        # make the command exactly 12 bytes.
        command = self.command + b'\x00' * (12 - len(self.command))
        # we need to convert the payload length from int to LE bytes.
        payload_length = int_to_little_endian(len(self.payload), 4)
        payload = self.payload
        # compute the payload checksum, which is first 4 bytes of hash256 of payload.
        payload_checksum = hash256(self.payload)[:4]
        # return the concatenation
        return magic + command + payload_length + payload_checksum + payload

    # Returns a stream for parsing the payload.
    def stream(self):
        return BytesIO(self.payload)


class NetworkEnvelopeTest(TestCase):

    def test_parse(self):
        msg = bytes.fromhex('f9beb4d976657261636b000000000000000000005df6e0e2')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.command, b'verack')
        self.assertEqual(envelope.payload, b'')
        msg = bytes.fromhex('f9beb4d976657273696f6e0000000000650000005f1a69d2721101000100000000000000bc8f5e5400000000010000000000000000000000000000000000ffffc61b6409208d010000000000000000000000000000000000ffffcb0071c0208d128035cbc97953f80f2f5361746f7368693a302e392e332fcf05050001')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.command, b'version')
        self.assertEqual(envelope.payload, msg[24:])

    def test_serialize(self):
        msg = bytes.fromhex('f9beb4d976657261636b000000000000000000005df6e0e2')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.serialize(), msg)
        msg = bytes.fromhex('f9beb4d976657273696f6e0000000000650000005f1a69d2721101000100000000000000bc8f5e5400000000010000000000000000000000000000000000ffffc61b6409208d010000000000000000000000000000000000ffffcb0071c0208d128035cbc97953f80f2f5361746f7368693a302e392e332fcf05050001')
        stream = BytesIO(msg)
        envelope = NetworkEnvelope.parse(stream)
        self.assertEqual(envelope.serialize(), msg)


# When a node creates an outgoing connection, it will immediately advertise its version.
# The remote node will respond with its version.
# No further communication is possible until both peers have exchanged their version.
class VersionMessage:

    command = b'version'

    def __init__(self, version=70015, services=b'\r\x04\x00\x00\x00\x00\x00\x00', timestamp=None, receiver_services=b'\r\x04\x00\x00\x00\x00\x00\x00',
                 receiver_ip=b'\x00\x00\x00\x00', receiver_port=8333, sender_services=b'\r\x04\x00\x00\x00\x00\x00\x00',
                 sender_ip=b'\x7f\x00\x00\x01', sender_port=8333, nonce=None,
                 user_agent=b'/Satoshi:0.18.1/', latest_block=0, relay=False):
        # Identifies protocol version being used by the node.
        self.version = version
        # features to be enabled for this connection.
        self.services = services
        # standard UNIX timestamp in seconds.
        if timestamp is None:
            self.timestamp = int(time.time())
        else:
            self.timestamp = timestamp
        self.receiver_services = receiver_services
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.sender_services = sender_services
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        # Node random nonce, randomly generated every time a version packet is sent.
        # This nonce is used to detect connections to self.
        if nonce is None:
            self.nonce = int_to_little_endian(randint(0, 2**64), 8)
        else:
            self.nonce = nonce

        self.user_agent = user_agent
        # The last block received by the emitting node.
        self.latest_block = latest_block
        # Whether the remote peer should announce relayed transactions or not, see BIP 0037.
        # If it's set to 0 it tells the full node not to send transaction messages unless they match
        # a bloom filter or they have been specifically requested - page 216.
        self.relay = relay

    # returns the VersionMessage in bytes format.
    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += self.services
        # result += int_to_little_endian(self.services, 8)
        result += int_to_little_endian(self.timestamp, 8)
        result += self.receiver_services
        # result += int_to_little_endian(self.receiver_services, 8)
        result += b'\x00' * 10 + b'\xff\xff' + self.receiver_ip
        result += int_to_little_endian(self.receiver_port, 2)
        result += self.sender_services
        # result += int_to_little_endian(self.sender_services, 8)
        result += b'\x00' * 10 + b'\xff\xff' + self.sender_ip
        result += int_to_little_endian(self.sender_port, 2)
        result += self.nonce
        result += encode_varint(len(self.user_agent))
        result += self.user_agent
        result += int_to_little_endian(self.latest_block, 4)
        if self.relay:
            result += b'\x01'
        else:
            result += b'\x00'
        return result

    @classmethod
    def parse(cls, stream):
        version = little_endian_to_int(stream.read(4))
        services_bytes = stream.read(8)
        print('bitfield', bytes_to_bit_field(services_bytes))
        services = little_endian_to_int(services_bytes)
        timestamp = little_endian_to_int(stream.read(8))
        receiver_services_bytes = stream.read(8)
        print('rs bitfield', bytes_to_bit_field(receiver_services_bytes))
        receiver_services = little_endian_to_int(receiver_services_bytes)
        receiver_ip = stream.read(12)
        receiver_port = little_endian_to_int(stream.read(2))
        sender_services_bytes = stream.read(8)
        print('ss bitfield', bytes_to_bit_field(sender_services_bytes))
        sender_services = little_endian_to_int(sender_services_bytes)
        sender_ip = stream.read(12)
        sender_port = little_endian_to_int(stream.read(2))
        nonce = stream.read(8)
        user_agent_length = read_varint(stream)
        user_agent = stream.read(user_agent_length)
        latest_block = little_endian_to_int(stream.read(4))
        relay = stream.read(1)
        return cls(version, services, timestamp, receiver_services, receiver_ip, receiver_port,
                   sender_services, sender_ip, sender_port, nonce, user_agent, latest_block, relay)


# The verack message is sent in reply to version.
# This message consists of only a message header with the command string "verack".
class VerAckMessage:

    command = b'verack'

    def __init__(self):
        pass

    @classmethod
    def parse(cls, s):
        return cls()

    def serialize(self):
        return b''


# The ping message is sent primarily to confirm that the TCP/IP connection is still valid.
# An error in transmission is presumed to be a closed connection and the address is removed as a current peer.
class PingMessage:

    command = b'ping'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


# The pong message is sent in response to a ping message.
# In modern protocol versions, a pong response is generated using a nonce included in the ping.
class PongMessage:

    command = b'pong'

    def __init__(self, nonce):
        self.nonce = nonce

    @classmethod
    def parse(cls, s):
        nonce = s.read(8)
        return cls(nonce)

    def serialize(self):
        return self.nonce


# Message to ask for block headers - page 184.
class GetHeadersMessage:

    command = b'getheaders'

    def __init__(self, version=70015, num_hashes=1, start_block=None, end_block=None):
        # Identifies protocol version being used by the node.
        self.version = version
        # We're going to assume that the number of block header groups is 1.
        # A more robust implementation would be able to handle more than 1.
        self.num_hashes = num_hashes
        # Hash of the start block header.
        if start_block is None:
            raise RuntimeError("A start block is required.")
        self.start_block = start_block
        # Hash of the last desired block header; set to zero to get as many blocks as possible
        if end_block is None:
            self.end_block = b'\x00' * 32
        else:
            self.end_block = end_block

    # Returns bytes serialization of the GetHeadersMessage object.
    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += encode_varint(self.num_hashes)
        # start and end block are already in bytes, so we just convert them to LE.
        result += self.start_block[::-1]
        result += self.end_block[::-1]
        return result

    # Receives a stream of bytes and returns a GetHeadersMessage object.
    @classmethod
    def parse(cls, stream):
        version = little_endian_to_int(stream.read(4))
        num_hashes = read_varint(stream)
        start_block = stream.read(32)[::-1]
        end_block = stream.read(32)[::-1]
        return cls(version, num_hashes, start_block, end_block)


# When we ask for some headers with a getheaders command (GetHeadersMessage), the other node will
# reply with a headers command. That's why we create this class. To handle that response - page 186.
class HeadersMessage:

    command = b'headers'

    def __init__(self, blocks):
        # List with Block objects.
        self.blocks = blocks

    @classmethod
    def parse(cls, stream):
        # The headers message starts with the number of headers as a varint.
        num_headers = read_varint(stream)
        # We need to append each block to this list.
        blocks = []
        for _ in range(num_headers):
            # Each block is parsed with the Block's class parse method using the same stream.
            blocks.append(Block.parse(stream))
            # The number of txs is always 0 and is remnant of block parsing.
            num_txs = read_varint(stream)
            if num_txs != 0:
                raise RuntimeError('number of transactions not 0.')
        return cls(blocks)


# Class to create a GenericMessage object. The command and payload can be passed as arguments to create the
# message.
class GenericMessage:

    def __init__(self, command, payload):
        self.command = command
        self.payload = payload

    def serialize(self):
        return self.payload


# The getdata command is what communicates blocks and transactions. This is the message used to ask for
# transactions, blocks, merkle blocks or compaact block - page 217.
class GetDataMessage:

    command = b'getdata'

    def __init__(self):
        self.data = []

    def add_data(self, data_type, identifier):
        # We add items we want to the message using this method. The data type indicates if it's a tx,
        # block, filtered block or compact block. Each type has a unique value.
        self.data.append((data_type, identifier))

    # Returns the message payload - page 217.
    def serialize(self):
        payload = encode_varint(len(self.data))
        for data_type, identifier in self.data:
            payload += int_to_little_endian(data_type, 4)
            payload += identifier[::-1]
        return payload


class BlockMessage:

    command = b'block'

    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce, txn_count, txns):
        self.version = version
        self.prev_block = prev_block
        self.merkle_root = merkle_root
        self.timestamp = timestamp
        self.bits = bits
        self.nonce = nonce
        self.txn_count = txn_count
        self.txns = txns

    @classmethod
    def parse(cls, stream):
        version = little_endian_to_int(stream.read(4))
        prev_block = stream.read(32)[::-1]
        merkle_root = stream.read(32)[::-1]
        timestamp = little_endian_to_int(stream.read(4))
        bits = stream.read(4)
        nonce = stream.read(4)
        txn_count = read_varint(stream)
        txns = []
        for _ in range(txn_count):
            txns.append(Tx.parse(stream))
        return cls(version, prev_block, merkle_root, timestamp, bits, nonce, txn_count, txns)
    
    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += self.prev_block[::-1]
        result += self.merkle_root[::-1]
        result += int_to_little_endian(self.timestamp, 4)
        result += self.bits
        result += self.nonce
        result += encode_varint(self.txn_count)
        for txn in self.txns:
            result += txn.serialize()
        return result


class SimpleNode:

    # port and host are the port and host we want to connect to.
    def __init__(self, host, port=None, testnet=False, logging=False):
        if port is None:
            if testnet:
                port = 18333
            else:
                port = 8333
        self.testnet = testnet
        self.logging = logging
        # socket.socket() is used to create a socket object.
        # AF_INET is the Internet address family for IPv4.
        # we specify the socket type (2nd argument) as socket.SOCK_STREAM because
        # when you do that, the default protocol that’s used is the Transmission Control Protocol (TCP).
        # This is a good default and probably what you want.
        # TCP relieves you from having to worry about packet loss, data arriving out-of-order,
        # and many other things that invariably happen when you’re communicating across a network.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect() is used to connect to the server. host is the server's IP address and port is the
        # port used by the server.
        self.socket.connect((host, port))
        # we create a stream to be able to read from the socket. A stream made this way can be
        # passed to all the parse methods - page 181.
        self.stream = self.socket.makefile('rb', None)

    # send a message to the connected node.
    def send(self, message):
        # the command property and serialize method are expected to exist in the message object - page 183.
        envelope = NetworkEnvelope(
            message.command, message.serialize(), self.testnet)
        if self.logging:
            print(f"sending: {envelope}")
        self.socket.sendall(envelope.serialize())

    # reads a new mesage from the socket - page 182.
    def read(self):
        envelope = NetworkEnvelope.parse(self.stream, testnet=self.testnet)
        if self.logging:
            print(f"receiving: {envelope}")
        return envelope

    # lets us wait for any one of several messages (message classes) - page 183.
    # note: a commercial-strength would not use something like this.
    def wait_for(self, *message_classes):
        command = None
        command_to_class = {m.command: m for m in message_classes}
        # loop until the command is in the commands we want.
        while command not in command_to_class.keys():
            # get the next network message.
            envelope = self.read()
            print('envelope', envelope)
            # set the command to be evaluated.
            command = envelope.command
            print('command', command)
            # we know how to respond to version and ping, handle that here.
            if command == VersionMessage.command:
                print('VersionMessage', envelope.payload)
                self.send(VerAckMessage())
            elif command == PingMessage.command:
                self.send(PongMessage(envelope.payload))
        # return the envelope parsed as a member of the right message class.
        return command_to_class[command].parse(envelope.stream())

    # The network handshake is how nodes establish communication - page 181.
    # Handshake is sending a version message and getting a verack back.
    def handshake(self):
        # First step is to send a version message to the node we want to connect to.
        version = VersionMessage()
        print('bitfield 2', bytes_to_bit_field(version.services))
        print('rs bitfield 2', bytes_to_bit_field(version.receiver_services))
        print('ss bitfield 2', bytes_to_bit_field(version.sender_services))
        self.send(version)
        version_msg = self.wait_for(VersionMessage)
        # The node we are connecting to receives the version message and responds with a verack message.
        self.wait_for(VerAckMessage)
