import time
import socket
from random import randint
from lib import compute_checksum, double_sha256

ZERO = b'\x00'
IPV4_PREFIX = b"\x00" * 10 + b"\x00" * 2
dummy_address = {
    "services": 0,
    "ip": '0.0.0.0',
    "port": 8333
}

def ip_to_bytes(ip):
    if ":" in ip:
        return socket.inet_pton(socket.AF_INET6, ip)
    else:
        return IPV4_PREFIX + socket.inet_pton(socket.AF_INET, ip)

def serialize_address(address, has_timestamp):
    result = b""
    if has_timestamp:
        result += int_to_little_endian(address['timestamp'], 8)
    result += int_to_little_endian(address['services'], 8)
    result += ip_to_bytes(address['ip'])
    result += int_to_big_endian(address['port'], 2)
    return result

def int_to_little_endian(integer, length):
    return integer.to_bytes(length, 'little')
def int_to_big_endian(integer, length):
    return integer.to_bytes(length, 'big')
    
def services_dict_to_int(services_dict):
    key_to_multiplier = {
        'NODE_NETWORK': 2**0,
        'NODE_GETUTXO': 2**1,
        'NODE_BLOOM': 2**2,
        'NODE_WITNESS': 2**3,
        'NODE_NETWORK_LIMITED': 2**10,
    }
    total= 0
    
    for key, val in services_dict.items():
        total += int(val) * key_to_multiplier.get(key, 0)
    return total
        

def bool_to_bytes(bool):
    return int_to_little_endian(int(bool), 1)
    
def serialize_varint(i):
    if i < 0xfd:
        return bytes([i])
    elif i < 256**2:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 256**4:
        return b'\xfe' + int_to_little_endian(i,4)
    elif i < 256**8:
        return b'\xff' + int_to_little_endian(i,8)
    else:
        raise RuntimeError('integer too large: {}'.format(i))
def serialize_varstr(bytes):
    return serialize_varint(len(bytes)) + bytes
    
# Try implementing yourself here:
# def compute_checksum(bytes):
#     raise NotImplementedError()
    
def serialize_version_payload(
        version=70015, services=0, timestamp=None,
        receiver_address=dummy_address,
        sender_address=dummy_address,
        nonce=None, user_agent=b'/buidl-army/',
        start_height=0, relay=True, services_dict={}):
    if timestamp is None:
        timestamp = int(time.time())
    if nonce is None:
        nonce = randint(0, 2**64)
    # message starts empty, we add to it for every field
    msg = b''
    # version
    msg += int_to_little_endian(version, 4)
    # services
    msg += int_to_little_endian(services_dict_to_int(services_dict),8)
    # timestamp
    msg += int_to_little_endian(timestamp, 8)
    # receiver address
    msg += serialize_address(address=receiver_address, has_timestamp=False)
    # sender address
    msg += serialize_address(address=sender_address, has_timestamp=False)
    # nonce
    msg += int_to_little_endian(nonce, 8)
    # user agent
    msg += serialize_varstr(user_agent)
    # start height
    msg += int_to_little_endian(start_height,4)
    # relay
    msg += bool_to_bytes(relay)
    return msg 

def serialize_message(command, payload):
    #network magic
    result = b'\xf9\xbe\xb4\xd9'
    # command
    result += command + b'\x00' * (12 - len(command))
    # length     
    result += int_to_little_endian(len(payload), 4)
    # checksum
    result += compute_checksum(payload)
    #payload
    result += payload
    return result

def handshake(address):
    sock = socket.create_connection(address, timeout=1)
    stream = sock.makefile("rb")

    # Step 1: our version message
    sock.sendall("OUR VERSION MESSAGE")
    print("Sent version")

    # Step 2: their version message
    peer_version = "READ THEIR VERSION MESSAGE HERE"
    print("Version: ")
    print(peer_version)

    # Step 3: their version message
    peer_verack = "READ THEIR VERACK MESSAGE HERE"
    print("Verack: ", peer_verack)

    # Step 4: our verack
    sock.sendall("OUR VERACK HERE")
    print("Sent verack")

    return sock, stream