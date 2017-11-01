import sys
import serial.tools.list_ports
from binascii import unhexlify, hexlify
from threading import Event
from Queue import Queue
import time
import api


class Central(api.Central):
    def __init__(self, port):
        api.Central.__init__(self, port)
        self._c_rx_buf = Queue()

    def on_cli_text_received(self, text):
        for c in text:
            self._c_rx_buf.put(c)

    def read(self, n=1, timeout=1):
        expiry = time.time() + timeout
        data = ''
        while n != 0:
            timeout = expiry - time.time()
            if timeout < 0:
                break
            try:
                ch = self._c_rx_buf.get(timeout=timeout)
                if ch:
                    n -= 1
                    data += ch
            except:
                pass
        return data

    def flush(self):
        self._c_rx_buf.queue.clear()

    def write(self, data):
        self.cmd_cli(data.decode('utf-8'))

    def close(self):
        self.disconnect()
