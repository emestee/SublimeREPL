import dev_bencode as bencode
import dev_bdecode as bdecode

import socket
import signal

BUF_SIZE = 4096

class BencodeStreamSocket():
    def __init__(self, sock):
        self.socket = sock
        self.tail = None
        self.daemon = True

    def send(self, val):
        self.socket.sendall(bencode.bencode(val))

    def recv(self):
        """Read a single full bencode entity. Block until one is attained."""
        decoded = None

        while decoded is None:
            if self.tail:
                decoded, self.tail = bdecode.loads(self.tail)
                if decoded: 
                    return decoded

            bytes = self.socket.recv(BUF_SIZE)

            if not bytes:
                # Socket was closed
                return None

            if self.tail:
                # Retain the tail for next iteration or call.
                bytes = self.tail + bytes

            decoded, self.tail = bdecode.loads(bytes)

        return decoded