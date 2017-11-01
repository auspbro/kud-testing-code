"""
Copyright (C) 2016, Synapse Product Development, LLC

This unpublished material is proprietary to Synapse Product
Development, LLC. All rights reserved. The methods and
techniques described herein are considered trade secrets
and/or confidential. Reproduction or distribution, in whole
or in part, is forbidden except by express written permission
of Synapse Product Development, LLC.

OVERVIEW:
    This API is designed as a test BLE Client-side framework. The intention is to provide basic
    functionality such as scanning, connecting, reading, writing, etc to help accelerate
    writing test code in the situation where a mock BLE client is needed. The API includes four primary abstractions:
    clients, connections, characteristics and chracteristic deligates. This particular framework is built on top of
    BlueGiga's BGAPI and designed and tested with the BLED112.

CLIENT:
    The client module's primary responsibilty is to discover & maintian connections with peripheral devices.
    The interface provides ways that the user can interact with, instantiate, and query connection objects.

CONNECTION:
    Connection objects keep track of the services & characteristics associated with a particular device.
    Through connections, the user can list and instantiate its characteristics.

CHARACTERISTIC:
    Characteristic modules are the primary way to communicate with particular device. Through these abstractions,
    the user can read/write to different characteristics to grab data.

CHARACTERISTIC DELEGATE:
    The delegate abstraction is meant to be implemented by the tester. Write project-specific functions in this
    abstraction to inject specialized functionality to interact with the data being communicated from particular devices

"""

import time
import binascii
from bgapi import api, cmd_def, module
from bgapi.cmd_def import connection_status_mask,RESULT_CODE
from bgapi.module import BlueGigaModule, GATTCharacteristic, GATTService, BlueGigaClient, BlueGigaServer
from binascii import hexlify
import uuid
from struct import pack


###################BLE CLIENT INTERFACE#####################
"""
Derrived from BGAPI's BlueGigaClient
"""
class bleCentral(module.BlueGigaClient):
    def __init__(self, port, baudrate, timeout, trace_enable = False):
        super(bleCentral, self).__init__(port, baudrate, timeout)
        self.CONNECTION_OBJECT = bleConnection #overriding connection object factory
        self._responses = [] #list of client advertisement responses
        self.trace_enable = trace_enable #trace enabled
        self.reset_ble_state() #reset BLED112

    def _parseScanResponses(self):
        """
        parse a list of responses
        """
        if not self.scan_responses:
            return []

        response_hash = {}
        for resp in self.scan_responses:
            # sender address + packet_type consitutes unique response
            response_hash[resp.sender + str(resp.packet_type)] = resp

        return [resp for resp in response_hash.itervalues()]

    def _doScanning(self, _scan, timeout, active):
        """
        template scanning function
        """
        self.reset_ble_state()
        if active: self.active_scan()
        _scan(timeout)
        if active: self.disable_scan()


    def scanAll(self, timeout = 5, active = True):
        """
        Scan for advertising devices
        @args - timeout: scanning T/O
        """
        self._doScanning(self.scan_all, timeout, active)


    def scanGeneral(self, timeout = 5, active = True):
        """
        Scan for advertising devices
        @args - timeout: scanning T/O
        """
        self._doScanning(self.scan_general, timeout, active)


    def scanLimited(self, timeout = 5):
        """
        Scan for advertising devices
        @args - timeout: scanning T/O
        """
        self._doScanning(self.scan_limitted, timeout, active)


    """ uncomment for debug prints
    def ble_evt_gap_scan_response(self, rssi, packet_type, sender, address_type, bond, data):
        module.BlueGigaClient.ble_evt_gap_scan_response(self, rssi, packet_type, sender, address_type, bond, data)
        print "rssi:%s packet_type:%s sender:%s address_type:%s bond:%s payload=%s" \
            %(str(rssi), str(packet_type), hexlify(sender), str(address_type), str(bond), hexlify(data))
    """

    def getResponses(self):
        """
        List all of the responses returned durning scanning
        """
        return self._parseScanResponses()


    def getResponseData(self):
        """
        List device info for response
        """
        return [resp.data for resp in self._parseScanResponses()]


    def getKnownPeripheralMacAddresses(self):
        """
        List device info for response
        """
        return [resp.sender for resp in self._parseScanResponses()]


    def connectByResponse(self, resp, timeout=5):
        """
        Connection helper function
        """
        connection = self.connect(target=resp, conn_interval_min=20, conn_interval_max=40)
        if connection == None:
            self._trace("No connection found")
            return

        connection.resp_timeout = timeout
        connection.central = self
        connection._populateAttributes(resp.data)
        return connection

    def connectByAdvertisementData(self, data):
        """
        create a connection based on advertisement data
        """
        found = None

        for resp in self.getResponses():
            if data in resp.data:
                found = resp
                break

        if found:
            return self.connectByResponse(found)

        return found

    def connectByAddress(self, addr):
        """
        Create a connection by device address
        @args - addr: device address
        """
        found = None
        self._trace("Testing Connection...")
        for resp in self._parseScanResponses():
            if addr == resp.sender:
                found = self.connectByResponse(resp)
                break
        return found

    def disconnectDevice(self, connection):
        """
        Disconnect from a device
        @args - addr: device address
        """
        self.disconnect(connection.handle)

    def getConnectionsAddresses(self):
        """
        Returns a list of connections maintained by the Client by address
        """
        array = []
        for target in self.connections.itervalues():
            array.append(hexlify(target.address))
        return array

    def getConnectionsDeviceInfo(self):
        """
        Returns a list of connections maintained by the Client by device info
        """
        array = []
        for target in self.connections.itervalues():
            array.append(target.device_info)
        return array

    def getConnectionByAddress(self, addr):
        """
        Returns a maintained connection
        @args - addr: device address
        """
        for handle, target in self.connections.iteritems():
            if addr == hexlify(target.address):
                return target
        return None

    def getAddressbyDeviceInfo(self, dev):
        """
        Returns a maintained connection
        @args - dev: device info
        """
        for handle, target in self.connections.iteritems():
            if dev in target.device_info:
                return hexlify(target.address)
        return None

    ########## NOT USER INVOKED ############
    def ble_evt_attclient_attribute_value(self, connection, atthandle, type, value):
        """
        Invoked when a packet is recieved from a device
        """
        super(bleCentral, self).ble_evt_attclient_attribute_value(connection, atthandle, type, value)
        self.connections[connection]._on_attribute_value_updated(atthandle, type, value)

    def _trace(self, arg):
        """
        Invoked when user passes a trace argument from the command line
        """
        if self.trace_enable:
            print arg



##################BLE CONNECTION INTERFACE######################
"""
Derrived from BGAPI's BLEConnection
"""
class bleConnection(module.BLEConnection):
    def __init__(self, api, handle, address, address_type, interval, timeout, latency, bonding):
        module.BLEConnection.__init__(self, api, handle, address, address_type, interval, timeout, latency, bonding)

    def close(self):
        """
        disconnect from the peripheral
        """
        self.central.disconnect(self)


    def getServices(self):
        """
        List all the services associated with a particular connection
        """
        array = []
        for s in self.services:
            if hexlify(s.PRIMARY_SERVICE_UUID) not in array:
                array.append(hexlify(s.PRIMARY_SERVICE_UUID))
            if hexlify(s.SECONDARY_SERVICE_UUID) not in array:
                array.append(hexlify(s.SECONDARY_SERVICE_UUID))
        return array

    def getCharacteristicUUIDs(self):
        """
        List all the characteristics associated with a particular connection
        """
        chars = [value.uuid for (key, value) in self.characteristics.iteritems()]
        return [hexlify(s) for s in chars]

    def getCharacteristicByUUID(self, u):
        """
        Get a characteristic associated with a connection by its UUID
        @args - u: characteristic UUID
        """
        #print "+UUID:%s" %hexlify(u)
        for (key, value) in self.characteristics.iteritems():
            try:
                #print "*UUID:" + hexlify(value.uuid)
                if value.uuid == u:
                    return value
            except:
                pass

    def getCharacteristicByHandle(self, handle):
        """
        Get a characteristic associated with a connection by its handle
        @args - handle: characteristic handle
        """
        return self.characteristics[handle]

    ########## NOT USER INVOKED ############
    def update_handle(self, handle, value):
        """
        Invoked by BGAPI to update characteristic handles upon reception of data
        """
        if handle in self.handle_uuid:
            if self.handle_uuid[handle] == GATTCharacteristic.CHARACTERISTIC_UUID:
                self.characteristics[handle] = bleCharacteristic(handle, value, self)
            else:
                for characteristic in self.get_characteristics()[::-1]:
                    if characteristic.handle < handle:
                        characteristic.add_descriptor(self.handle_uuid[handle], handle, value)
                        break
        else:
            raise BlueGigaModuleException("Attribute Value for Handle %d received with unknown UUID!" % (handle))
        if handle in self.attrclient_value_cb:
            self.attrclient_value_cb[handle](value)

    def _populateAttributes(self, data):
        """
        Invoked upon construction of a connection to acquire all attributes associated with the connection
        """
        self.device_info = data
        self.read_by_group_type(module.GATTService.PRIMARY_SERVICE_UUID, self.resp_timeout)
        self.services = self.get_services()
        for s in self.services:
            self.find_information(s)
            self.read_by_type(s, module.GATTCharacteristic.CHARACTERISTIC_UUID, self.resp_timeout)
            self.read_by_type(s, module.GATTCharacteristic.CLIENT_CHARACTERISTIC_CONFIG, self.resp_timeout)
            self.read_by_type(s, module.GATTCharacteristic.USER_DESCRIPTION, self.resp_timeout)

    def _on_attribute_value_updated(self, atthandle, type, value):
        """
        Invoked when data is recieved from a characteristic
        """
        try:
            #print "value_updated %d %s" %(atthandle, hexlify(value))
            #print "got-value: %s" %value


            characteristic = self.getCharacteristicByHandle(atthandle - 1) #NOTE: Read handle is write handle - 1 (BGAPI mechanics?) -- May be buggy
            characteristic.onAsyncReadResp(value)
        except:
            pass

    def write_noresp_by_handle(self, handle, data):
        """
        Invoked by the characteristic interface to write to that characteristic

        """
        #print "write %d" %handle


        self.start_procedure(module.PROCEDURE)
        self._api.ble_cmd_attclient_write_command(self.handle, handle, data)

    def write_by_handle(self, handle, value, timeout=3):
        self.start_procedure(module.PROCEDURE)
        self._api.ble_cmd_attclient_attribute_write(self.handle, handle, value)
        if not self.wait_for_procedure(timeout=timeout):
            raise module.BlueGigaModuleException("Write did not complete before timeout! Connection:%d - Handle:%d" % (self.handle, handle))


###############BLE CHARACTERISTIC DELEGATE#################
class bleCharacteristicDelegate:
    """
     Implemented by client's to inject functionality into the bleCharacteristic
     FIXME: IMPLEMENT OTHER FUNCTIONALITY HERE
    """
    def onAsyncReadResp(self, data):
        """
        called asyncronously when an indication/notification of data is received
        FIXME: IMPLEMENT
        """


##############BLE CHARACTERISTIC INTERFACE#################
"""
Derrived from BGAPI's GATTCharacteristic
"""
class bleCharacteristic(module.GATTCharacteristic):
    def __init__(self, handle, properties, conRef):
        super(bleCharacteristic, self).__init__(handle, properties)
        self.delegate = bleCharacteristicDelegate() #User injected code
        self.connectionRef = conRef #Reference to the associated connection

    def getUUID(self):
        """
        Returns this characteristic's UUID
        """
        return str(uuid.UUID(bytes = self.uuid))

    def getHandle(self):
        """
        Returns this characteristic's handle
        """
        return self.handle

    def read(self):
        """
        Read from the characteristic
        """
        self.connectionRef.read_by_handle(handle = self.handle + 1)

    def subscribe(self, indications=True, notifications=True):
        """
        Subscribe to specified parameters
        """
        self.connectionRef.characteristic_subscription(self, indicate=indications, notify=notifications)

    def subscribeToReceiveIndicationsOnly(self):
        """
        subscribe for inndications
        """
        self.subscribe(notifications=False)

    def subscribeToReceiveNotificationsOnly(self):
        """
        subscribe for notifications
        """
        self.subscribe(indications=False)

    def writeNoResp(self, data):
        """
        Write to this characteristic with no response
        @args - data: data to be written
        """
        self.connectionRef.write_noresp_by_handle(handle = self.handle + 1, data = data) # (...+ 1) write handle?

    def writeWithResp(self, data, timeout=5.0):
        """
        write to the charactersitic and wait for ack
        """
        self.connectionRef.write_by_handle(self.handle + 1, data, timeout)


    ########## NOT USER INVOKED ############
    def onAsyncReadResp(self, data):
        """
        Invoked when data is recieved from this characteristic. Functionality handled by delegate.
        """
        self.delegate.onAsyncReadResp(data)
