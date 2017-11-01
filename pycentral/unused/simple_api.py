"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
from domain_manager import domain_manager
from cobs_transport import cobs_transport
from central import EikCentral
from struct import pack, unpack

# This UUID is a combination of BLE_UUID_VALUE_CHARACTERISTIC_UUID and BLE_UUID_BASE_UUID found in template_service.h
# It is set in _add_readwrite_parameter() in template_service_readwrite.c
API_UUID = UUID("00000012D5798DE51E0844A5A33351BE").bytes[::-1]
CLI_UUID = UUID("00000013D5798DE51E0844A5A33351BE").bytes[::-1]


class ApiCompletion(object):
    """
    used to store a procedure to be executed when the API function return
    """
    def __init__(self, handler):
        self._handler = handler

    def on_complete(self, data):
        """
        handle the on_complete event
        """
        (msg_type,) = unpack('B', data[0])
        if self._handler:
            self._handler(msg_type, data[1:])


def api_default_handler(msg_type, data):
    print "type:%d value:'%s'" %(msg_type, data)

class Api(object):
    def __init__(self):
        pass

    def connect(self):
        """
        connect to the central
        """
        self._central = EikCentral(baudrate=115200, timeout=5)
        self._central.connect()

        # open the characteristics
        api_char = self._central.char_get(API_UUID)
        api_char.onAsyncReadResp = self._on_api_rx_data
        api_char.subscribeToReceiveNotificationsOnly()


        cli_char = self._central.char_get(CLI_UUID)
        cli_char.onAsyncReadResp = self.on_cli_text_received
        cli_char.subscribeToReceiveNotificationsOnly()

        self._transport = cobs_transport(api_char,
                                        server_rx_buffer_size=1023,
                                        tx_block_size=20)

    def on_cli_text_received(self, note):
        """
        handle receiving text from the CLI
        """
        print hexlify(note)

    def disconnect(self):
        """
        disconnect from the central
        """
        self._phy.disconnect()

    def send(self, msg_type, data, handler=api_default_handler):
        """
        send data with specified message type
        """
        self._domain.send(pack('<B', msg_type) + data, ApiCompletion(handler))

    def cmd_loopback(self, data):
        self.send(msg_type=0, data=data)


if __name__ == "__main__":
    api = Api()
    api.connect()
    api.cmd_loopback("hello world!")
