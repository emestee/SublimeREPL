import dev_bencode as bencode
import dev_bdecode as bdecode

import socket
import signal

BUF_SIZE = 128

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
            bytes = self.socket.recv(BUF_SIZE)

            if not bytes:
                # Socket was closed
                return None

            if self.tail:
                # Retain the tail for next iteration or call.
                bytes = self.tail + bytes

            decoded, self.tail = bdecode.loads(bytes)

        return decoded

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4567))

    ss = BencodeStreamSocket(s)
    while True:
        data = ss.recv()
        if data is None:
            break

        print "DECODED:", data

    #s.shutdown()
    s.close()
