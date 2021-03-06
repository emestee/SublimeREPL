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
        self._debug_send = False

    def send(self, val):
        val = bencode.bencode(val)
        if self._debug_send:
            print val
        self.socket.sendall(val)

    def disconnect(self):
        self.socket.close()
        self.socket = None

    def recv(self):
        """Read a single full bencode entity. Block until one is attained."""
        decoded = None

        while decoded is None:
            if self.tail:
                decoded, self.tail = bdecode.loads(self.tail)
                if decoded: 
                    return decoded

            try:
                bytes = self.socket.recv(BUF_SIZE)
            except socket.error:
                return None

            if not bytes:
                # Socket was closed
                return None

            if self.tail:
                # Retain the tail for next iteration or call.
                bytes = self.tail + bytes

            decoded, self.tail = bdecode.loads(bytes)

        return decoded