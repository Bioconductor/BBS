#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: May 13, 2011
###
###
### jobs module
###

import sys
import os
import errno
import subprocess
import signal
import datetime
import time
import socket
if sys.platform == "win32":
    import psutil
    #import win32api
    #from win32com.client import GetObject
    #for i in range(10):
    #    try:
    #        WMI = GetObject('winmgmts:')
    #    except:
    #        if i == 9:
    #            sys.exit("BBS>   FATAL ERROR: GetObject('winmgmts:') failed 10 times => EXIT.")
    #        print("BBS>   GetObject('winmgmts:') failed. ", end=" ")
    #        print("Trying again in 1 sec.")
    #        win32api.Sleep(long(1000))
    #    else:
    #        break

sys.path.insert(0, os.path.dirname(__file__))
import parse

##############################################################################
## On Windows XP time.sleep() is fragile: if the Python script is started by
## the Task Scheduler, then it dies when the user it is run as logs in during
## a call to time.sleep().
##############################################################################

def sleep(secs):
    #if sys.platform == "win32":
    #    win32api.Sleep(long(secs * 1000))
    #else:
    time.sleep(secs)


##############################################################################
## Subprocess.
##############################################################################

def call(cmd, check=False):
    # If we don't flush now, stuff that has already been sent to stdout by
    # this script can appear after stuff printed to stdout by subprocess...
    sys.stdout.flush()
    # Nasty things (that I don't really understand) happen with
    # subprocess.call() if this script is started by Schedule on Windows
    # (the child process tends to almost always return an error).
    # Apparently using "stderr=subprocess.STDOUT" fixes this pb.
    retcode = subprocess.call(cmd, stderr=subprocess.STDOUT, shell=True)
    if check and retcode != 0:
        raise subprocess.CalledProcessError(retcode, cmd)
    return retcode

### Implementation taken from subprocess.check_output() (available in Python
### >= 2.7 only).
def getCmdOutput(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        sys.exit("BBS>   FATAL ERROR: subprocess '%s' returned nonzero value %d\nBBS>   and generated error message:\nBBS>     %s" % (cmd, retcode, output))
    return parse.bytes2str(output)

def doOrDie(cmd):
    retcode = call(cmd)
    if retcode == 0:
        return
    sys.exit("BBS>   FATAL ERROR: subprocess '%s' returned nonzero value %d!" % (cmd, retcode))

#if sys.platform == "win32":
if False:
    # Helpful places to look at when it comes to manipulate the list of active
    # processes:
    #   http://mail.python.org/pipermail/python-win32/2003-December/001482.html
    #   http://mail.python.org/pipermail/python-win32/2009-September/009542.html
    #   http://www.blog.pythonlibrary.org/2010/10/03/how-to-find-and-list-all-running-processes-with-python/
    def getAllActivePIDs():
        processes = WMI.InstancesOf('Win32_Process')
        all_PIDs = []
        for proc in processes:
            PID = proc.ProcessID
            all_PIDs.append(PID)
        return all_PIDs
    def getProcByPID(pid):
        query = "select * from Win32_Process where ProcessID=%d" % pid
        processes = WMI.ExecQuery(query)
        if len(processes) > 1:
            # Should never happen.
            sys.exit("BBS>   FATAL ERROR: More than 1 process with PID %d?! Something's serously going wrong!" % pid)
        if len(processes) == 0:
            return None
        return processes[0]
    def printProcProperties(proc):
        print("BBS>     Process properties for PID %d:" % proc.ProcessID)
        for prop in proc.Properties_:
            print("BBS>     | - %s: %s" % (prop.Name, prop.Value))
        return
    # Parents are listed *after* all their children in the returned list.
    # Returns None if 'pid' is an invalid process id.
    def listSubprocs(pid):
        processes = WMI.InstancesOf('Win32_Process')
        pid_exists = False
        for proc in processes:
            procid = proc.ProcessID
            if procid == pid:
                pid_exists = True
                break
        if not pid_exists:
            return None  # invalid process id
        def listSubprocs_rec(proc):
            proc_id = proc.ProcessID
            proc_creation_date = proc.CreationDate
            children = []
            for child in processes:
                child_parent_id = child.ParentProcessId
                if child_parent_id != proc_id:
                    continue
                ## Looking at ParentProcessId only is not enough to determine
                ## the parent-child relationship. For example, we could imagine
                ## that an orphan process A fires a child process B and that
                ## the pid assigned to B is the same as the pid that was
                ## assigned to the parent of A (the parent of A was killed so
                ## now its pid is available and can be re-used). I don't know
                ## if this is a realistic example though. Anyway, in that case,
                ## by looking at the ParentProcessId property only, A is the
                ## parent of B and B *looks* like the parent of A.
                ## If we also look at the CreationDate property, A is the
                ## parent of B (because B was created *after* A) but B is not
                ## the parent of A. More generally speaking, comparing the
                ## CreationDate properties should make the parent-child graph
                ## look acyclic (except for those processes that are their own
                ## parent, see below) and therefore avoid infinite recursion in
                ## the listSubprocs_rec() function (a case of such infinite
                ## recursion has been observed for the 1st time on one Windows
                ## build machine after more than 4 months of running the builds
                ## with the old version of listSubprocs_rec()).
                child_creation_date = child.CreationDate
                if child_creation_date < proc_creation_date:
                    continue
                child_id = child.ProcessID
                ## Avoid infinite recursion when a process is its own parent
                ## (like the process with PID=0 on Windows):
                if child_id == child_parent_id:
                    continue
                children += listSubprocs_rec(child)
            children.append(proc)
            return children
        return listSubprocs_rec(proc)

def killProc(pid):
    if sys.platform != "win32":
        # On Solaris, this kills only the shell, but the command passed
        # in cmd keeps running in the background!
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError as e:
            if e.errno == 3:
                print("BBS>   No such process: %s" % pid)
            else:
                print("BBS>   Error %s killing process %s" % (e.errno, pid))
            return
        return

    # For now, on windows, try using the psutil module to kill a process
    # and its children recursively, because we have been having
    # trouble using TASKKILL to do this. Eventually consider replacing
    # all the process-related code in this file with psutil.
    # Of course, the build machines must have this module installed
    # (it's not installed by default).
    # Note that the kill() method preemptively checks to see if the PID
    # has been reused, protecting against killing a different
    # process than the one you wanted to kill. See
    # https://pythonhosted.org/psutil/#psutil.Process.kill

    # The process represented by 'pid' may already have been killed,
    # but it could still have children. Since 'proc' would be
    # None in this case, we can't call proc.children(), so walk over
    # psutil.process_iter() to find the children. And let's find the
    # children before we kill the parent.
    children = []
    for proc in psutil.process_iter():
        try:
            if proc.ppid() == pid:
                children.append(proc)
        except psutil.NoSuchProcess:
            pass

    # Let's start the mass murdering...
    try:
        print("BBS>     killing %s" % pid)
        proc = psutil.Process(pid)
        proc.kill()
    except psutil.NoSuchProcess:
        print("BBS>     No such process %s."  % pid)
    except psutil.AccessDenied:
        print("BBS>     Access denied (pid=%s)."  % pid)
    except TypeError:
        sys.exit("BBS>     pid must be an integer! (got %s)" % pid)

    for child in children:
        try:
            print("BBS>       killing child %s" % child.pid)
            grandkids = child.children(recursive=True)
            child.kill()
            for grandkid in grandkids:
                try:
                    print("BBS>         killing grandkid %s" % grandkid.pid)
                    grandkid.kill()
                except psutil.NoSuchProcess:
                    print("BBS>         Grandkid process %s does not exist." % grandkid.pid)
                except psutil.AccessDenied:
                    print("BBS>         Access denied (pid=%s)."  % grandkid.pid)
        except psutil.NoSuchProcess:
            print("BBS>       Child process %s does not exist." % child.pid)
        except psutil.AccessDenied:
            print("BBS>       Access denied (pid=%s)."  % child.pid)

### What if cmd is not found, can't be started or crashes?
def runJob(cmd, stdout=None, maxtime=2400.0, verbose=False):
    if verbose:
        print("BBS>   runJob(): " + cmd)
    if stdout == None:
        out = None
    else:
        out = open(stdout, 'w')
    t1 = time.time()
    ## IMPORTANT: Because of shell=True, Popen() starts (at least) 2
    ## subprocesses:
    ## - on Unix: a shell AND the command passed in cmd,
    ## - on Windows: "cmd.exe" AND the command passed in cmd.
    ## The command passed in cmd is started as a child of the shell
    ## (or "cmd.exe").
    proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT, shell=True)
    if verbose:
        ## IMPORTANT: Which PID is returned by proc.pid?
        ##   - on Linux: it's the PID of the command passed in cmd,
        ##   - on Solaris: it's the PID of the shell,
        ##   - on Windows: it's the PID of the "cmd.exe" command.
        sys.stdout.write("BBS>     pid = %d / time [" % proc.pid)
    sys.stdout.flush()
    nloop = 0
    timeout = False
    while proc.poll() == None:
        dt = time.time() - t1
        if dt > maxtime:
            timeout = True
            break
        sleep(0.1)
        nloop += 1
        if verbose and nloop % 100 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
    if verbose:
        dt = time.time() - t1
        sys.stdout.write("] = %.2f seconds / " % dt)
    if timeout:
        retcode = None
        if verbose:
            print("TIMEOUT!")
        ## killProc() raises an OSError if passed an invalid process ID.
        ## Note that this could very well happen if the process terminates
        ## after the last call to proc.poll() and before we call
        ## killProc(proc.pid).
        try:
            killProc(proc.pid)
        except OSError:
            pass
    else:
        retcode = proc.wait()
        if verbose:
            sys.stdout.write("retcode = %d / " % retcode)
            if retcode != 0:
                print("ERROR!")
            else:
                print("OK")
    if stdout != None:
        out.close()
    return retcode

def tryHardToRunJob(cmd, nb_attempts=1, stdout=None, maxtime=60.0, sleeptime=20.0, failure_is_fatal=True, verbose=False):
    for i in range(nb_attempts):
        retcode = runJob(cmd, stdout, maxtime, verbose)
        if retcode == 0:
            return 0
        sleep(sleeptime)
    if failure_is_fatal:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sys.exit("%d failed attempts => EXIT at %s." % (nb_attempts, now))
    print("%d failed attempts => never mind, let's keep going..." % nb_attempts)
    return retcode

### Objects passed to the processJobQueue() function must be QueuedJob objects.
### The QueuedJob class contains the strictly minimal stuff needed by the
### processJobQueue() in order to work.
### If a queued job returns in time, processJobQueue() will call RerunMe() and,
### if True, will rerun the job. If it returns in time again, then
### processJobQueue() will call RerunMe() again and so on... until RerunMe()
### returns False or the job does not return in time (time out). Then either
### AfterRun() or AfterTimeout() is called.
### If you want the RerunMe(), AfterRun() and/or AfterTimeout() methods to do
### something more useful than what the default methods below do, then you need
### to derive the "QueuedJob" class and provide your own implementation for
### these methods.
class QueuedJob:
    def __init__(self, name, cmd, output_file):
        self._name = name                # Job name.
        self._cmd = cmd                  # Command to execute (or None).
        self._output_file = output_file  # Where to capture std out and err.
    def RerunMe(self):
        False
    def AfterRun(self):
        if self._retcode == 0:
            cumul_inc = 1
        else:
            cumul_inc = 0
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        pass

class JobQueue:
    def __init__(self, name, jobs, job_deps):
        self._name = name          # Queue name e.g. 'buildsrc' etc...
        self._jobs = jobs          # List of QueuedJob objects.
        self._job_deps = job_deps  # None or a dict with 1 entry per job.
                                   # Each entry lists the deps of the job
                                   # i.e. which other jobs in the queue
                                   # must be processed before this job.

def _unprocessedDeps(deps, processed_jobs):
    unprocessed_deps = []
    for dep in deps:
        if not dep in processed_jobs:
            unprocessed_deps.append(dep)
    return unprocessed_deps

def _getNextJobToProcess(job_queue, processed_jobs, nb_busy_slots):
    jobs = job_queue._jobs
    job_deps = job_queue._job_deps
    if job_deps == None:
        job_rank = len(processed_jobs) + nb_busy_slots
        job = jobs[job_rank]
        return job
    # Look for a job in the queue that is waiting to be processed (i.e. has
    # no '_rank' attribute) and for which all deps have already been processed.
    for job in jobs:
        if hasattr(job, '_rank'):
            continue
        unprocessed_deps = _unprocessedDeps(job_deps[job._name], processed_jobs)
        if len(unprocessed_deps) == 0:
            job._unprocessed_deps = unprocessed_deps
            return job
    # We couldn't find one. That means that all the waiting jobs are blocked
    # because of deps that still need to be processed. If 'nb_busy_slots' != 0,
    # this could be just temporary so we return None and we'll have to try
    # later:
    if nb_busy_slots != 0:
        return None
    # However, if 'nb_busy_slots' == 0, that means the unprocessed deps are
    # circular deps or deps on unknown packages. In that case we return the
    # first waiting job in the queue and we attach the unprocessed deps to it:
    for job in jobs:
        if hasattr(job, '_rank'):
            continue
        unprocessed_deps = _unprocessedDeps(job_deps[job._name], processed_jobs)
        job._unprocessed_deps = unprocessed_deps
        return job
    # Should never get here (would happen only if no more jobs in the queue
    # are waiting to be processed and 'nb_busy_slots' is 0).
    sys.exit("BBS>   FATAL ERROR in _getNextJobToProcess(): Unexpectedly reached end of function.")

def _logActionOnQueuedJob(action, job, nb_jobs, nb_slots, job_deps=None):
    print()
    msg = "%s JOB %s (%d/%d)" % (action, job._name, job._rank+1, nb_jobs)
    if nb_slots != 1:
        msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
    print("bbs.jobs.processJobQueue> %s" % msg)
    if job_deps != None:
        print("bbs.jobs.processJobQueue>   Deps:", end=" ")
        print(job_deps[job._name])
        print("bbs.jobs.processJobQueue>   Unprocessed deps:", end=" ")
        print(job._unprocessed_deps)
    print("bbs.jobs.processJobQueue>   Command: %s" % job._cmd)

def _writeRunHeader(out, cmd, nb_runs):
    if nb_runs != 1:
        out.write("\n\n\n")
    for i in range(0, 78):
        out.write("#")
    out.write("\n")
    for i in range(0, 78):
        out.write("#")
    out.write("\n")
    out.write("###\n")
    if nb_runs == 1:
        out.write("### Running")
    else:
        out.write("### Re-running")
    out.write(" command:\n")
    out.write("###\n")
    out.write("###   %s\n" % cmd)
    out.write("###\n")
    for i in range(0, 78):
        out.write("#")
    out.write("\n")
    for i in range(0, 78):
        out.write("#")
    out.write("\n")
    out.write("\n\n")
    out.flush()

def _runQueuedJob(job, verbose, nb_jobs, nb_slots, job_deps):
    if verbose:
        _logActionOnQueuedJob("START", job, nb_jobs, nb_slots, job_deps)
    job._t1 = job._t2 = time.time()
    job._startedat = dateString(time.localtime(job._t1))
    job._output = open(job._output_file, 'w')
    job._nb_runs = 1
    _writeRunHeader(job._output, job._cmd, job._nb_runs)
    job._proc = subprocess.Popen(job._cmd, stdout=job._output,
                                 stderr=job._output, shell=True)
    if verbose and nb_slots == 1:
        ## IMPORTANT: Which PID is stored in job._proc.pid?
        ##   - on Linux: it's the PID of the command passed in cmd,
        ##   - on Solaris: it's the PID of the shell,
        ##   - on Windows: it's the PID of the "cmd.exe" command.
        sys.stdout.write(" [pid=%d/" % job._proc.pid)
    sys.stdout.flush()
    return job

def _rerunQueuedJob(job, verbose, nb_jobs, nb_slots):
    if verbose:
        _logActionOnQueuedJob("RESTART", job, nb_jobs, nb_slots)
    job._output = open(job._output_file, 'a')
    job._nb_runs += 1
    _writeRunHeader(job._output, job._cmd, job._nb_runs)
    job._proc = subprocess.Popen(job._cmd, stdout=job._output,
                                 stderr=job._output, shell=True)
    if verbose and nb_slots == 1:
        ## IMPORTANT: Which PID is stored in job._proc.pid?
        ##   - on Linux: it's the PID of the command passed in cmd,
        ##   - on Solaris: it's the PID of the shell,
        ##   - on Windows: it's the PID of the "cmd.exe" command.
        sys.stdout.write(" [pid=%d/" % job._proc.pid)
    sys.stdout.flush()
    return job

### Returns 0 if job is still running, 1 if it returned in time, and -1 if
### it timed out.
def _checkQueuedJobStatus(job, maxtime_per_job, verbose, nb_jobs, nb_slots):
    job._t2 = time.time()
    dt = job._t2 - job._t1
    if job._proc.poll() == None:
        if dt < maxtime_per_job:
            return 0
        killProc(job._proc.pid)
        if verbose:
            if nb_slots == 1:
                print("/TIMEOUT!]")
            else:
                print()
                msg = "KILL JOB %s (%d/%d)" % (job._name, job._rank+1, nb_jobs)
                msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
                msg += " after %.2f seconds" % dt
                print("bbs.jobs.processJobQueue> %s" % msg)
        return -1
    job._retcode = job._proc.wait()
    if verbose:
        if nb_slots == 1:
            if job._retcode == 0:
                print("/OK]")
            else:
                print("/ERROR!/retcode=%d]" % job._retcode)
        else:
            print()
            msg = "DONE JOB %s (%d/%d)" % (job._name, job._rank+1, nb_jobs)
            msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
            msg += " after %.2f seconds [retcode=%d]" % (dt, job._retcode)
            print("bbs.jobs.processJobQueue> %s" % msg)
    return 1

def _logSlotEvent(logfile, event_type, job0, slot0, slots):
    date = currentDateString()
    logfile.write("\n")
    logfile.write("===============================================================================\n")
    logfile.write("%s event on SLOT %s/%s on %s:\n" % \
                  (event_type, slot0 + 1, len(slots), date))
    logfile.write("  - job name: %s\n" % job0._name)
    logfile.write("  - job command: %s\n" % job0._cmd)
    logfile.write("  - job output file: %s\n" % job0._output_file)
    logfile.write("-------------------------------------------------------------------------------\n")
    for slot in range(len(slots)):
        logfile.write("SLOT %s:" % (slot + 1))
        job = slots[slot]
        if job != None:
            dt = job._t2 - job._t1
            logfile.write(" %s [pid=%d / StartedAt: %s / %.1f seconds ago]" % (job._name, job._proc.pid, job._startedat, dt))
        logfile.write("\n")
    logfile.flush()
    return

def _logSummaryOfJobsWithUnprocessedDeps(job_queue):
    print("bbs.jobs.processJobQueue> %s" % \
          "Jobs with unprocessed deps at time of processing:")
    jobs = job_queue._jobs
    job_deps = job_queue._job_deps
    i = 0
    for job in jobs:
        unprocessed_deps = job._unprocessed_deps
        if len(unprocessed_deps) == 0:
            continue
        i += 1
        msg = "JOB %s (%d/%d)" % (job._name, job._rank+1, len(jobs))
        print("bbs.jobs.processJobQueue>   %s" % msg)
        print("bbs.jobs.processJobQueue>     Deps:", end=" ")
        print(job_deps[job._name])
        print("bbs.jobs.processJobQueue>     Unprocessed deps:", end=" ")
        print(job._unprocessed_deps)
        print("bbs.jobs.processJobQueue>     Command: %s" % job._cmd)
    if i != 0:
        print("bbs.jobs.processJobQueue>   Total = %d" % i)
    else:
        print("bbs.jobs.processJobQueue>   %s" % None)
    return

### Process 'job_queue' (a JobQueue object) in parallel.
### Will run at most 'nb_slots' jobs simultaneously.
def processJobQueue(job_queue, nb_slots=1,
                    maxtime_per_job=3600.0, verbose=False):
    jobs = job_queue._jobs
    job_deps = job_queue._job_deps
    nb_jobs = len(jobs)
    if verbose:
        print()
        print("bbs.jobs.processJobQueue>", end=" ")
        print("%d jobs in the queue. Start processing them using %d slots" % \
              (nb_jobs, nb_slots))
    slotevents_logfile = open(job_queue._name + '-slot-events.log', 'w')
    processed_jobs = []
    nb_busy_slots = 0
    slots = nb_slots * [None]
    loop = -1
    slot = -1
    cumul = 0
    while len(processed_jobs) < nb_jobs:
        slot += 1
        if slot == nb_slots:
            sleep(0.5)
            slot = 0
        job = slots[slot]
        loop += 1
        if job != None:
            status = _checkQueuedJobStatus(job, maxtime_per_job, verbose,
                                           nb_jobs, nb_slots)
            if status == 0: # still running
                if verbose and nb_slots == 1 and loop % 10 == 0:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                continue
            job._output.close()
            if status == 1: # returned in time
                if job.RerunMe():
                    sleep(5.0)
                    slots[slot] = _rerunQueuedJob(job, verbose,
                                                  nb_jobs, nb_slots)
                    continue
                job._endedat = dateString(time.localtime(job._t2))
                cumul += job.AfterRun()
            else: # timed out
                job._endedat = dateString(time.localtime(job._t2))
                job.AfterTimeout(maxtime_per_job)
            processed_jobs.append(job._name)
            slots[slot] = None
            nb_busy_slots -= 1
            _logSlotEvent(slotevents_logfile, 'REMOVE', job, slot, slots)
        # Slot 'slot' is available
        while True:
            job_rank = len(processed_jobs) + nb_busy_slots
            if job_rank == nb_jobs:
                # All the jobs are either already processed or currently being
                # processed.
                break
            job = _getNextJobToProcess(job_queue, processed_jobs, nb_busy_slots)
            # 'job == None' means we couldn't get a job to process now but
            # we should wait and try again later.
            if job == None:
                break
            job._rank = job_rank
            if job._cmd != None:
                job._slot = slot
                slots[slot] = _runQueuedJob(job, verbose, nb_jobs, nb_slots,
                                            job_deps)
                nb_busy_slots += 1
                _logSlotEvent(slotevents_logfile, 'ASSIGN', job, slot, slots)
                break
            # SKIP the job
            if verbose:
                _logActionOnQueuedJob("SKIP", job, nb_jobs, 1, job_deps)
            processed_jobs.append(job._name)
    slotevents_logfile.close()
    if verbose:
        print()
        print("bbs.jobs.processJobQueue> Finished.")
        if job_deps != None:
            _logSummaryOfJobsWithUnprocessedDeps(job_queue)
        print()
    return cumul


##############################################################################
## Other stuff
##

def getHostname():
    if sys.platform == "win32":
        computername = os.environ['COMPUTERNAME'].lower()
        if "USERDNSDOMAIN" in os.environ:
            computername += "." + os.environ['USERDNSDOMAIN'].lower()
        return computername
    hostname = socket.gethostname()
    #if hostname[-1] == '\n':
    #    hostname = hostname[0:-1]
    hostname = hostname.lower()
    hostname = hostname.replace(".local", "")
    hostname = hostname.replace(".fhcrc.org", "")
    hostname = hostname.replace(".bioconductor.org", "")
    return hostname

## Formatted date+time.
## 'tm' must be a <type 'time.struct_time'> object as returned by
## time.localtime(). See http://docs.python.org/lib/module-time.html
## for more info.
## Example:
##   >>> dateString(time.localtime())
##   '2007-12-07 10:03:15 -0800 (Fri, 07 Dec 2007)'
## Note that this is how 'svn log' and 'svn info' format the dates.
def dateString(tm):
    if tm.tm_isdst:
        utc_offset = time.altzone # 7 hours in Seattle
    else:
        utc_offset = time.timezone # 8 hours in Seattle
    utc_offset /= 3600
    format = "%%Y-%%m-%%d %%H:%%M:%%S -0%d00 (%%a, %%d %%b %%Y)" % utc_offset
    return time.strftime(format, tm)

def currentDateString():
    return dateString(time.localtime())


if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")
