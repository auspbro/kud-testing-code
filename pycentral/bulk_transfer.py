from struct import pack, unpack
from threading import Event
from binascii import hexlify
from Queue import Queue
(TR_STATUS_OK,
TR_STATUS_PAGE_INVALID,
TR_STATUS_PAGE_IN_USE,
TR_STATUS_PAGE_CORRUPT,
TR_STATUS_INVALID_FILE_HANDLE) = range(5)

(MSG_TYPE_PAGE_GET,
MSG_TYPE_PAGE_PUT,
MSG_TYPE_FILE_ERASE,
MSG_TYPE_FILE_PROPS,
MSG_TYPE_SYSTEM_RESET,
MSG_TYPE_COUNT) = range(6)

def ti_header_get(img):
  crc0, crc1 = unpack('<HH', img[:4])
  ver, length, garbage, offset, imgType, status = unpack('<HHIIBB', img[4:18])
  imgType = 0 # metadata does not exist yet
  status = 0xFF
  return pack('<HHHHIIBB',
              crc0, crc0, ver, length, garbage, offset, imgType, status)


class BulkTransferAgent:
    def __init__(self, api):
        self._api = api
        self._img = ''
        self._status = TR_STATUS_OK

    def get(self, handle):
        """
        get the resource specified by the handle
        """
        self._status = TR_STATUS_OK
        self._img = ''
        evt = Event()
        evt.clear()
        def on_page_rxed(msg_type, reply):
            status, length = unpack('BB', reply[:2])
            self._status = status
            if status == TR_STATUS_OK:
                self._img += reply[2:2+length]
            evt.set()
        page_id = 0
        while self._status == TR_STATUS_OK:
            descriptor = pack('<BH', handle, page_id)
            self._api.bulk_transfer_send(MSG_TYPE_PAGE_GET, descriptor, on_page_rxed)
            evt.wait()
            evt.clear()
            page_id += 1
        if self._status == TR_STATUS_PAGE_INVALID:
            return self._img
        return None

    def erase(self, handle):
        """
        erase the file specified
        """
        evt = Event()
        evt.clear()
        def on_erased(msg_type, data):
            evt.set()
        handle = pack('B', handle)
        self._api.bulk_transfer_send(MSG_TYPE_FILE_ERASE, handle, on_erased)
        evt.wait(1)

    def _put_page(self, evt, handle, page_id, page):
        def on_page_acked(msg_type, reply):
            if msg_type & 0x80:
                print 'error will robinson'
            status, = unpack('B', reply)
            self._status = status
            evt.put(1)
        page = pack('<BHB', handle, page_id, len(page)) + page
        self._api.bulk_transfer_send(MSG_TYPE_PAGE_PUT, page, on_page_acked)


    def put(self, handle, blob):
        """
        get the resource specified by the handle
        """
        self._status = TR_STATUS_OK
        evt = Queue()
        evt.put(0)
        evt.put(1)
        page_id = 0
        base = 0
        end = 0
        PAGE_SIZE = 64
        while (self._status == TR_STATUS_OK) and (base < len(blob)):
            print page_id
            end = base + PAGE_SIZE
            if end > len(blob):
                end = len(blob)
            page = blob[base:end]
            evt.get(block=True)
            self._put_page(evt, handle, page_id, page)

            page_id += 1
            base = end

        if self._status != TR_STATUS_OK:
            print "failed!!!!"
            return False
        elif handle == 2: # OTA image handle
            print "success"
            # hack to write TI header (this should go away when we finish
            # cleaning up the TI bootloader)
            page_id = 0x78000 / PAGE_SIZE
            evt.get(block=True)
            self._put_page(evt, handle, page_id, ti_header_get(blob))
            evt.get(block=True)
            evt.get(block=True)
        return True

    def _blocking_send(self, msg_type, tx_data='', timeout=2):
        evt = Event()
        evt.clear()
        self._rx_data = ''
        def on_reply(msg_type, data):
            self._rx_data = data
            evt.set()
            pass
        self._api.bulk_transfer_send(msg_type, tx_data, on_reply)
        evt.wait(timeout)
        return self._rx_data

    def reset(self):
        self._blocking_send(MSG_TYPE_SYSTEM_RESET)
