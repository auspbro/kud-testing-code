"""
@copyright (c) 2016-2017 Synapse Product Development LLC ("Synapse").
All Rights Reserved. This file is subject to the terms and conditions
defined in the license obtained by you from Synapse.
"""
import time
from binascii import unhexlify
from api import Central
import sys

# string to match in the advertisement data
DEVICE_ID = "AnovaNano"

# The default port used by the Bluegiga device

COM = "COM7"



central = Central(COM)
central.connect(adv_data=DEVICE_ID)

for i in range(5):
	central.cmd_loopback("hello world!")
	time.sleep(1)
