import zerorpc
import yaml
import sys, os
import time
import re

zrpc_c = zerorpc.Client()
zrpc_c.connect("tcp://127.0.0.1:4242")

def extractresults(regex, resp):
    matches = re.finditer(regex, resp, re.MULTILINE)
    results = []
    for matchNum, match in enumerate(matches):
        matchNum = matchNum + 1
        values = []
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            values.append(match.group(groupNum))
            # Sakia add : to debug Regex and Results.
            print "item:" + str(matchNum-1) + ", index:" + str(groupNum-1) + ", value:" + str(match.group(groupNum))
        results.append(values)
    return results

def outputresult(test, result_list):
    try:
        path = r'.\Results'
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print e
        pass
    with open(os.path.join(path,"%s.cmd" % test.test_id), 'w') as out_file:
        for k in result_list.keys():
            out_file.write("SET %s=%s\n" % (k, result_list[k]))

def Commander(test,args):
    if args.has_key("Cmds"):
        result_list = {}
        for c in args['Cmds']:
            if c.has_key("Cmd"):
                print '>>> Run Command : %s  <<<"' %c['Cmd']
                resp = zrpc_c.send_cmd(c['Cmd'])
            elif c.has_key("Fun"):
                print '>>> Run Function : %s  <<<"' %c['Fun']
                if c['Args']:
                    resp = globals()[c['Fun']](test,c['Args'])
                else:
                    resp = globals()[c['Fun']](test,None)

#            if c['Cmd'] == 'ReImgInf':
#                resp = "Linux Ver: 3.13.0-32 \r\n Image Ver: 1.00"
#            if c['Cmd'] == 'ReWBTMAC':
#                resp = "WIFI: 08002763196b \r\n BT: E1335F734205"

            if c.get('Duration'):
                duration_sec = int(c['Duration'])
                time.sleep(duration_sec)
                resp = zrpc_c.ser_read(1024) #will timeout after a second
                
            print '>>> Run Result : %s <<<' %resp
            
            if c.get('Replace'):
                resp = resp.replace(c['Replace'][0], c['Replace'][1])
                
            print '>>> Run Replace : %s <<<' %resp
            
            if c.get('Results'):
                if c.get('Regex'):
                    results = extractresults(c['Regex'], resp)
                else:
                    results = resp
                    
                print '>>> Run Regex : %s <<<' %results
                
                for r in c['Results']:
                    if r['type'] == 'int':
                        try:
                            result_list[r['name']] = int(results[r['item']][r['index']])
                        except:
                            result_list[r['name']] = ''
                    elif r['type'] == 'float':
                        try:
                            result_list[r['name']] = float(results[r['item']][r['index']])
                        except:
                            result_list[r['name']] = ''
                    else:
                        try:
                            result_list[r['name']] = results[r['item']][r['index']]
                        except:
                            result_list[r['name']] = ''
                            
                    if result_list[r['name']] != '' and c.get('Unit'):
                        result_list[r['name']] = str(result_list[r['name']]) + c.get('Unit')
                #workaround
                if result_list.get('BLE_MAC_ADDR') is not None:
                    result_list['BLE_MAC_ADDR'] = "".join(reversed([result_list['BLE_MAC_ADDR'][i:i+2] for i in xrange(0,len(result_list['BLE_MAC_ADDR']),2)]))

            if c.get('SleepTime'):
                time.sleep(c.get('SleepTime'))
               
#        print result_list
#        for k, v in result_list.items():
#            print(k, v)
        
        if len(result_list) > 0:
            outputresult(test, result_list)
            return result_list
    else:
        return False

    return True

    
class Test:
    def __init__(self, params):
        self.params = params
        self.test_id = params['Name']
        self.instructions = params['Instructions']
        self.main_proc = self.load_proc_from_meta(params)

    def load_proc_from_meta(self, meta):
        proc = Commander
        args = meta['Args']
        return proc, args

    def action(self):
        proc, args = self.main_proc
        result = proc(self, args)
        return result


TestMetaDataTab = []
try:
    with open(sys.argv[1], 'r') as f:
        TestMetaDataTab += yaml.load(f)
except Exception, e:
    print "Failed to load test case file: [%s]" %sys.argv[1]
    print e
    shutdown()
    sys.exit()

TestCaseTab = []
for metaData in TestMetaDataTab:
    try:
        TestCaseTab.append(Test(metaData))
    except Exception, e:
        print "Error loading test case data!"
        print "stack trace:"
        print e
        sys.exit()

for TestCase in TestCaseTab:
    TestCase.action()