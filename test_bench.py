from Queue import Queue
import sys
import test_procs
import yaml
import background_thread as job_runner
from settings import settings
Logger = test_procs.Logger
ProcHash = test_procs.__dict__

result_queue = Queue()

# TODO implement skip button

# Sakia note: TestRecordDutID is only used to test the test_proc.py response
do_PreTest_Flog = False  # if setting False, then don't run TestRecordDutID
# Sakia note: TestDutCompleted is only used to test the test_proc.py response
do_PostTest_Flog = True  # if setting False, then don't run TestDutCompleted, but no save log.yml


def shutdown():
    # shutdown the connection to the API
    test_procs.api.wait_until_read = False
    def job(): test_procs.api.shutdown()
    job_runner.post(job)
    job_runner.shutdown()
    print "bench_shutdown"

def dispatch_result(job):
    result_queue.put(job)

def dispatch_next():
    job = None
    try:
        job = result_queue.get(False)
    except:
        pass

    return job
#
# load the tests
#

def DefaultProc(test, args):
    """
    dummy defualt procedure
    """
    print "called default proc"
    return False

class Test:
    def __init__(self, params):
        self.params = params
        self.test_id = params['Name']
        self.instructions = params['Instructions']
        self.failure_description = "Test Failed!"
        self.passing_description = "Test Passed"
        if params.has_key('FailText'):
            self.failure_description = params['FailText']
        if params.has_key('PassText'):
            self.passing_description = params['PassText']
        self.values = ('', '', '')
        self.options = {}
        if params.has_key('Options'):
            if params['Options'] != None:
                self.options = params['Options']
        self.pre_test  = self.load_proc_explicit(params, 'PreTest')
        self.post_test = self.load_proc_explicit(params, 'PostTest')
        self.main_proc = self.load_proc_from_meta(params)
        if self.main_proc[0] == DefaultProc:
            self.failure_description = "Invalid test procedure loaded!"

    def load_proc_explicit(self, meta, name):
        proc = DefaultProc
        args = {}
        try:
            proc, args = self.load_proc_from_meta(meta[name])
        except:
            pass
        return proc, args

    def load_proc_from_meta(self, meta):
        proc = DefaultProc
        args = {}
        try:
            print meta['Proc']
            proc = ProcHash[meta['Proc']]
            try:
                args = meta['Args']
            except:
                pass
        except:
            pass
        print proc
        return proc, args

    def option_value(self, key):
        if self.options.has_key(key):
            return self.options[key]
        return None

    def action(self, on_complete):
        def job():
            proc, args = self.main_proc
            Logger.append_proc(proc.__name__, args)
            result = proc(self, args)
            Logger.mark(result)
            return result
        self.do_job(job, on_complete)

    def pre(self, on_complete=None):
        def job():
            proc, args = self.pre_test
            Logger.append_pre(proc.__name__, args)
            return proc(self, args)
        self.do_job(job, on_complete)

    def post(self, on_complete=None):
        print "do-post"
        def job():
            proc, args = self.post_test
            Logger.append_post(proc.__name__, args)
            return proc(self, args)
        self.do_job(job, on_complete)

    def do_job(self, job, on_complete):
        def worker():
            result = job()
            if on_complete:
                def post_result():
                    on_complete(result)
                dispatch_result(post_result)
        job_runner.post(worker)

class TestDutFinalize(Test):
    def __init__(self):
        Test.__init__(self,
            {
                'Name': 'TestDutCompleted',
                'Proc': 'Dummy',
                'PostTest' : {'Proc' : 'TestDutCompleted' },
                'Instructions' : 'Press <Next> to complete the test...',
                'Options' : { 'ConfigStep' : True }
            })

TestMetaDataTab = []

def load_test_list(path):
    global TestMetaDataTab
    try:
        with open(path, 'r') as f:
            TestMetaDataTab += yaml.load(f)
    except Exception, e:
        print "Failed to load test case file: [%s]" %path
        print e
        shutdown()
        sys.exit()

if do_PreTest_Flog:
    load_test_list(settings['TestBench']['PreTest']['Path'])  # TestRecordDutID, Sakia note: don't run PreTest to save time.

if len(sys.argv) >= 2:
    load_test_list(sys.argv[1])  # test_lists\temp.yml

TestCaseTab = []
for metaData in TestMetaDataTab:
    try:
        TestCaseTab.append(Test(metaData))
    except Exception, e:
        print "Error loading test case data!"
        print "stack trace:"
        print e
        sys.exit()
       
if do_PostTest_Flog:
    TestCaseTab.append(TestDutFinalize())  # TestDutCompleted, Sakia note: don't run TestDutFinalize to save time.

# Sakia note: show TestCase in simple_tester.py
# print len(TestCaseTab)  # -->> 3
# print TestCaseTab[0].values  # -->> TestRecordDutID
# print TestCaseTab[1].values  # -->> test_lists\temp.yml
# print TestCaseTab[2].values  # -->> TestDutCompleted

print "Loaded:"
for test in TestCaseTab:
    print " - %s" %test.test_id
