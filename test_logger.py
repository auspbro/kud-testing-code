import sys
import os
import datetime
import yaml
from settings import settings

debug_logger = 0

def time_stamp():
    return str(datetime.datetime.now())

class TestLog:
    def __init__(self):
        self.reset()

    def reset(self):
        self.log = []
        self.cur_proc_list = []
        self.cur_test = None
        self.cur_proc = None
        self.dut_id = ''
        self.provisioning_dut_id = False
        if debug_logger:    print "logger.reset()"


    def parse_results(self):
        test_results = {}
        # compute the final result for each test_id type
        for test in self.log:
            test_id = test['Name']
            # the last result shall be the final result
            result = True
            for proc in test['Results']:
                result = proc['Result']
            # mark the test result
            test_results.update({test_id: result})
        # compute the overall result
        result = True
        for key in test_results:
            result = result and test_results[key]
        if debug_logger:    print "logger.parse_results() : id = {}, resulte = {}".format(test_id, result)
        return result

    def append_test(self, name):
        self.cur_proc_list = []
        self.cur_test = {
            'Name': name,
            'Time': time_stamp(),
            'Results': self.cur_proc_list
        }
        self.log.append(self.cur_test)
        self.provisioning_dut_id = (name == 'TestRecordDutID')
        if debug_logger:    print "logger.append_test(name = {})".format(name)

    def append_proc(self, proc, args):
        self.cur_proc = {
            'Time': time_stamp(),
            'Proc': proc,
        }
        self.cur_proc_list.append(self.cur_proc)
        if debug_logger:    print "logger.append_proc(proc = {}, args = {})".format(proc, args)

    def append_post(self, proc, args):
        self.cur_test.update({'PostTest':
            {'Time': time_stamp(), 'Proc' : proc}
        })
        if debug_logger:    print "logger.aappend_post(proc = {}, args = {})".format(proc, args)

    def append_pre(self, proc, args):
        self.cur_test.update({'PreTest':
            {'Time': time_stamp(), 'Proc' : proc}
        })
        if debug_logger:    print "logger.append_pre(proc = {}, args = {})".format(proc, args)

    def record(self, values):
        self.cur_proc.update({'Values' : values})
        if self.provisioning_dut_id:
            self.dut_id = values
        if debug_logger:    print "logger.record(values = {})".format(values)

    def mark(self, state):
        self.cur_proc.update({'Result' : state})
        if debug_logger:    print "logger.mark(state = {})".format(state)


    def save(self, cli_log=None):
        result = 'failed'
        
        # Sakia note: parse_results() is check for any errors on log.yml, like "Result: false"
        if self.parse_results(): result = 'passed'
        try:
            path = settings['Logging']['Path']
            if not os.path.exists(path):
                    os.makedirs(path)
        except:
            pass
            
        # Sakia note: ts format -->> 2017_10_02__21_13_12
        ts = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
        if len(sys.argv) > 1:
            list_id = sys.argv[1].split('.')[0].split('\\')[-1]
            log_id = "%s_log_%s_%s_run_%s" %(list_id, self.dut_id, result, ts)
        else:
            log_id = "log_%s_%s_run_%s" %(self.dut_id, result, ts)
            
        log_name = '%s/mft_%s.yml' %(path, log_id)
        with open(log_name, 'w') as outfile:
            yaml.dump(self.log, outfile, default_flow_style=False)

        if cli_log:
            log_name = '%s/cli_%s.yml' %(path, log_id)
            with open(log_name, 'w') as outfile:
                yaml.dump(cli_log, outfile, default_flow_style=False)
            self.reset()
        if debug_logger:    print "logger.save(cli_log = {})".format(cli_log)
