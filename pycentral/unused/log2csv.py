import simplejson as json
import sys
#from pprint import pprint

data = ''
with open(sys.argv[1]) as data_file:
    data = json.load(data_file)


SENSORS_PROMPT = "Heater\tWaterLow\tWater\tInternal\tWaterLeak\tTriac"
CAP_TOUCH_PROMPT = "Button\tValue"

def sensor_to_csv(e):
    data =(
        e["Heater"],
        e["WaterLow"],
        float(e["Water"])/100,
        e["Internal"],
        e["WaterLeak"],
        e["Triac"])

    data = [str(d) for d in data]
    print '\t'.join(data)

def button_to_csv(e):
    data =(
        e["ButtonID"],
        e["CapValue"])
    data = [str(d) for d in data]
    print '\t'.join(data)


entries = data['Entries']





in_test = False
test_id = int(sys.argv[2])
if test_id == 0:
    print CAP_TOUCH_PROMPT
else:
    print SENSORS_PROMPT

for e in entries:
    category = e['Category']
    attrib = e['ID']
    if (category == 'TestState'):
        if int(e['Data'][0]) == test_id:
            in_test = True
        elif in_test:
            break
    elif in_test:
        if category == 'TestData':
            if attrib == 'Sensors':
                sensor_to_csv(e['Data'])
            elif attrib == 'ButtonPress':
                button_to_csv(e['Data'])
