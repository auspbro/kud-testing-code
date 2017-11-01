import test_bench
import time
import sys
import os
import background_thread as job_runner
import environ as env

do_SaveAsFiles_Flog = False

TestCaseTab = test_bench.TestCaseTab
Logger = test_bench.Logger
Settings = test_bench.settings
Logger.dut_id = Settings.get('SN')

# print len(sys.argv) # -->> 3
# print sys.argv[0]  # simple_tester.py
# print sys.argv[1]  # test_lists\temp.yml
# print sys.argv[2]  # true

if len(sys.argv) >= 3 and sys.argv[2].lower()=='true':
    do_SaveAsFiles_Flog = True

if do_SaveAsFiles_Flog:
    env.create_result_folder( Logger.dut_id )

def run_test(idx):
    print TestCaseTab[idx].test_id,">>"
    Logger.append_test(TestCaseTab[idx].test_id)
    TestCaseTab[idx].pre()
    def on_compelet(result):
        print '[========Compelet========]: '
        print 'test_id: ', TestCaseTab[idx].test_id
        print "test_cast: ", idx
        print "test_result: ", result
        if not (type(result) is bool):
            for key, value in result.items():
                print "  ", key, "->", value
#            print "\n",
        print '[========================]: '
        TestCaseTab[idx].post()

    TestCaseTab[idx].action(on_compelet) #push to work queue

print '[Start]'

'''
# Sakia note: no effect, really implemented in test_bench.py
TestCaseTab[1].values = sys.argv[2::]
'''
# print len(TestCaseTab)  # -->> 3
# print TestCaseTab[0].values  # -->> TestRecordDutID 
# print TestCaseTab[1].values  # -->> test_lists\temp.yml
# print TestCaseTab[2].values  # -->> TestDutCompleted

for idx in range(len(TestCaseTab)):
    try:
        run_test(idx)
        while(True):
            job = test_bench.dispatch_next()    #get on_compelet job
            if job != None:
                print
                job()
                break
            time.sleep(.1)
            #print '>',
        time.sleep(.1)
    except:
        print "main except!"
        break

print '[END]'

if do_SaveAsFiles_Flog:
    env.backup_result_folder( Logger.dut_id )

test_bench.shutdown()

# Sakia modiyf : used os._exit(0) to save time.
#sys.exit(0)
os._exit(0)
