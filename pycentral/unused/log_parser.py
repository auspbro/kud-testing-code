import time
import sys
from datetime import date
from struct import *
from binascii import *
import sys
import simplejson as json

HEADERSIZE = 8
MFT_TEST_DATA_TYPE_SENSORS = 0
MFT_TEST_DATA_TYPE_BUTTON_PRESS = 1

(LOG_CATEGORY_SYSTEM_STATUS,
 LOG_CATEGORY_SYSTEM_ERROR,
 LOG_CATEGORY_MFT_TEST_STATE,
 LOG_CATEGORY_MFT_TEST_DATA) = range(4)



def ParseSensor(packet):
    (Water, Heater, Triac, Internal,Water_Leak, Water_Low) = unpack('<HHHHHH', packet)
    return {
        'Water': Water,
        'Heater' : Heater,
        'Triac': Triac,
        'Internal' :Internal,
        'WaterLeak': Water_Leak,
        'WaterLow' : Water_Low}

def ParseButtonPress(packet):
    (ButtonID, Val) = unpack('<BH', packet)
    return {'ButtonID' : ButtonID, 'CapValue' : Val}

def ParseTestData(ID, blob):
    if ID == MFT_TEST_DATA_TYPE_SENSORS:
        ID = 'Sensors'
        blob = ParseSensor(blob)
    elif ID == MFT_TEST_DATA_TYPE_BUTTON_PRESS:
        ID = 'ButtonPress'
        blob = ParseButtonPress(blob)
    return ID, blob

def ParseTestState(ID, blob):
    (state,) = unpack('B', blob)
    state_tab = ['IDLE', 'RUNNING', 'DONE']
    test_tab = ['0-CapTouch', '1-TempAccuracy', '2-BurnIn']
    return state_tab[ID], test_tab[state]

def LogParsing(log_path):
    log = ''
    with open(log_path, 'rb') as f:
        log = f.read()
        f.close()
    log_rev, = unpack('<H', log[:2])
    log = log[2:]
    entries = []
    while log != '':
        (length, ID, category, timestamp) = unpack('<HBBI', log[:HEADERSIZE])
        log = log[HEADERSIZE:]
        length -= HEADERSIZE
        blob = log[:length]
        log = log[length:]
        cat = 'Unknown'
        sid = 'Unknown'
        rec = {}
        if category == LOG_CATEGORY_MFT_TEST_DATA:
            cat = "TestData"
            sid, rec = ParseTestData(ID, blob)
        elif category == LOG_CATEGORY_MFT_TEST_STATE:
            cat = "TestState"
            sid, rec = ParseTestState(ID, blob)
        entries.append({
            'Category' : cat,
            'ID' : sid,
            'Data' : rec,
        })
    f.close()

    with open(sys.argv[2], 'w') as f:
        json.dump({'LogRevision':log_rev, "Entries":entries}, f)
        f.close()

try:
    LogParsing(sys.argv[1])
except Exception, e:
    print "Log parse failure"
    print e

time.sleep(.2)
