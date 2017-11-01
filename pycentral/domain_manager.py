"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
from Queue import Queue
from struct import pack, unpack

class domain_context(object):
    """
    domain context object
    """
    def __init__(self, did, sender=None):
        self._id = did
        self._sender = sender

    def on_complete(self, datagram):
        # FIXME put this somewhere else
        if len(datagram) < 1:
            # FIXME handle this error condition
            return
        domain_id = datagram[:1]
        (domain_id,) = unpack('<B', domain_id)
        if (self._id == domain_id) and (self._sender != None):
            self._sender.on_complete(datagram[1:])


class domain(object):
    """
    represents a domain
    """
    def __init__(self, did, transport):
        self._id = did
        self._transport = transport

    def send(self, datagram, sender=None):
        """
        send the datagram to the domain manager
        """
        datagram = pack('<B', self._id) + datagram
        self._transport.send(datagram, domain_context(self._id, sender))



class domain_manager(object):
    """
    represents a domain manager
    """
    def __init__(self, transport):
        self._transport = transport

    def add_domain(self, domain_id):
        """
        install a new domain
        """
        return domain(domain_id, self._transport)
