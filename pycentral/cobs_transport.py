"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
import cobs
from Queue import Queue
from threading import Thread
from struct import pack, unpack
from binascii import hexlify


def buf_pack(buf):
    """
    pack the buffer
    """
    return pack('%dB' %len(buf), *buf)


def buf_unpack(buf):
    """
    unpack the buffer
    """
    return unpack('%dB' %len(buf), buf)


class cobs_transport_decoder(object):
    """
    manage the process of decoding a stream of frames
    """
    def __init__(self):
        self._buf = [] # temp buffer to hold
        self._idx = 0  # how much of the temp buffer has been processed?

    def process(self, data):
        """
        process input data
        """
        data = buf_unpack(data)
        self._buf += data
        frames = []
        while self._idx < len(self._buf):
            if self._buf[self._idx] == 0:
                # recovered a frame
                self._idx += 1
                fr = self._buf[:self._idx]
                fr = cobs.decode(fr)
                fr = buf_pack(fr)
                frames.append(fr)
                # remove frame from input
                self._buf = self._buf[self._idx:]
                self._idx = 0
            else:
                self._idx += 1
        return frames


class cobs_transport_encoder(object):
    """
    manage the process of encoding an object
    """
    def __init__(self):
        self._buf = '' # temp buffer to hold data

    def add(self, data):
        """
        append data to the encoder buffer
        """
        self._buf += data

    def encode(self):
        """
        compelete the encoding process and return the frame
        """
        fr = self._buf
        self._buf = ''
        fr = buf_unpack(fr)
        fr = cobs.encode(fr)
        return buf_pack(fr)


def segment(data, block_len=20):
    """
    chunk data for transport
    NOTE: this function assumes that input data consists of complete records
    """
    i = 0
    blocks = []
    end = len(data)
    while i < end:
        bl_end = i + block_len
        if bl_end > end:
            bl_end = end
        bl = data[i:bl_end]
        blocks.append(bl)
        i = bl_end
    return blocks


STATE_PENDING_TX = 0
STATE_WAIT_ACK   = 1

class cobs_transport_context(object):
    """
    context object to be handed back to sender
    """
    def __init__(self, tx_datagram, sender=None):
        self.state = STATE_PENDING_TX
        self.tx_datagram = tx_datagram
        self.rx_datagram = ''
        if sender != None:
            self.on_complete = sender.on_complete

    def on_complete(self, datagram):
        """
        handle consuming the datagram
        """
        pass


class cobs_transport(object):
    """
    represents a domain manager
    """
    def __init__(self,
                 phy,
                 server_rx_buffer_size,
                 tx_block_size=20):
        self._phy                   = phy
        self._encoder               = cobs_transport_encoder()
        self._decoder               = cobs_transport_decoder()
        self._rx_tx_queue           = Queue()
        self._tx_pending_queue      = Queue()
        self._rx_pending_queue      = Queue()
        self._server_rx_buffer_size = server_rx_buffer_size
        self._bytes_outstanding     = 0
        self._tx_block_size         = tx_block_size
        self._rx_data               = '' # received data
        self._thread                = Thread(target=self._run_rx_tx)
        self._phy.onAsyncReadResp   = self._on_receive
        self._thread.start()

    def shutdown(self):
        """
        shutdown the transport layer
        NOTE: need to create a new instance to connect again
        """
        self._rx_tx_queue.put(None)

    def send(self, datagram, sender=None):
        """
        send the datagram on the specified domain
        """
        self._encoder.add(datagram)
        datagram = self._encoder.encode()
        self._rx_tx_queue.put(cobs_transport_context(datagram, sender))

    def _tx_coroutine(self):
        """
        handle transmitting messages
        """
        data_to_send = ''
        while True:
            while self._tx_pending_queue.empty():
                # wait until there is data to process
                yield

            # grabe the next item and save it as a reply context
            ctx = self._tx_pending_queue.get()
            ctx.state = STATE_WAIT_ACK
            self._rx_pending_queue.put(ctx)

            # add the datagram to the data_to_send buffer
            data_to_send += ctx.tx_datagram
            # chop up the data to match the MTU of the BLE
            blocks = segment(data_to_send, self._tx_block_size)
            data_to_send = ''

            # transfer data to BLE block-by-block
            for bl in blocks:
                while self._bytes_outstanding > self._server_rx_buffer_size:
                    # ran out of space in the peripheral's buffer, so allow the
                    # receive path to run
                    yield

                if len(bl) < self._tx_block_size:
                    # got a fractional block -- try to glue this onto the next
                    # datagram (if one is staged)
                    empty = self._tx_pending_queue.empty()
                    while empty and (not self._rx_tx_queue.empty()):
                        # process all pending contexts before declaring empty
                        yield
                        empty = self._tx_pending_queue.empty()

                    if not empty:
                        # a datagram is staged, update data_to_send
                        # this block should be appended to the waiting datagram
                        data_to_send = bl
                        break

                # adjust the bytes outstanding to match
                self._bytes_outstanding += len(bl)

                # send data to physical layer device
                self._phy.writeNoResp(bl)


    def _run_rx_tx(self):
        """
        handle receive and transmit
        """
        # create a transmitter coroutine
        tx_c = self._tx_coroutine()

        while True:
            # wait for next context object from producors
            ctx = self._rx_tx_queue.get()
            if ctx == None:
                break

            if ctx.state == STATE_PENDING_TX:
                # stage data into the transmit FIFO
                self._tx_pending_queue.put(ctx)
            else:
                # handle receive case
                self._bytes_outstanding -= len(ctx.tx_datagram)
                ctx.on_complete(ctx.rx_datagram)

            # run the tranmit process
            tx_c.next()


    def _on_receive(self, data):
        """
        handle processing the input data
        """
        for datagram in self._decoder.process(data):
            # extract the datagram from the queue of outstanding contexts
            ctx = self._rx_pending_queue.get()
            ctx.rx_datagram = datagram
            # send the context to the tx/rx thread for final processing
            self._rx_tx_queue.put(ctx)
