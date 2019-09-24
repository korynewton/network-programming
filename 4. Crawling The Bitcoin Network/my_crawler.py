from io import BytesIO
from lib import handshake, read_msg, serialize_msg, read_varint, read_address

def read_addr_payload(stream):
    r = {}
    count = read_varint(stream)
    r['addresses'] = [read_address(stream) for _ in range(count)]
    
    return r
    
def listener(addresses):
    while True:
        # Get next address from addresses and connect 
        address = addresses.pop()
        try:
            # establish connection
            print(f'Connecting to {address}')
            sock = handshake(address)
            stream = sock.makefile('rb')
            
            # Request peer's peers
            sock.sendall(serialize_msg(b'getaddr'))
                    
            # Print every gossip message we receive
            while True:
                msg = read_msg(stream)
                command = msg['command']
                payload_len = len(msg['payload'])
                print(f'received a "{command}" containing {payload_len} bytes')
                
                # Respond to "ping"
                if command == b'ping':
                    res = serialize_msg(command=b'pong', payload=msg['payload'])
                    sock.sendall(res)
                    print('sent "pong"')

                #Specialty handle peer list
                if command == b'addr':
                    payload = read_addr_payload(BytesIO(msg["payload"]))
                    if len(payload['addresses']) > 1:
                        addresses.extend([
                           (a['ip'], a['port']) for a in payload['addresses']
                        ])
                        break
        except Exception as e:
            print(f'got error: {str(e)}')
            continue
if __name__ == '__main__':
    remote_addr = [('104.199.166.145', 8333)]
    #local_addr = 'localhost', 8333
    listener(remote_addr)
    
    

