from Queue import Queue
from threading import Thread


jobs = Queue()

def job_runner():
    while True:
        job = jobs.get()
        if job == None:
            break
        job()

job_thread = Thread(target=job_runner)
job_thread.start()

def post(job):
    jobs.put(job)

def shutdown():
    jobs.put(None)
