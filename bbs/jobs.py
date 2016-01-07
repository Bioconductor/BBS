#!/usr/bin/env python
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
if sys.platform == "win32":
    import win32api
    from win32com.client import GetObject
    for i in range(10):
        try:
            WMI = GetObject('winmgmts:')
        except:
            if i == 9:
                sys.exit("BBS>   FATAL ERROR: GetObject('winmgmts:') failed 10 times => EXIT.")
            print "BBS>   GetObject('winmgmts:') failed. ",
            print "Trying again in 1 sec."
            win32api.Sleep(long(1000))
        else:
            break
import time


##############################################################################
## On Windows XP time.sleep() is fragile: if the Python script is started by
## the Task Scheduler, then it dies when the user it is run as logs in during
## a call to time.sleep().
##############################################################################

def sleep(secs):
    if sys.platform == "win32":
        win32api.Sleep(long(secs * 1000))
    else:
        time.sleep(secs)


##############################################################################
## Subprocess.
##############################################################################

def call(cmd):
    # If we don't flush now, stuff that has already been sent to stdout by
    # this script can appear after stuff printed to stdout by subprocess...
    sys.stdout.flush()
    # Nasty things (that I don't really understand) happen with
    # subprocess.call() if this script is started by Schedule on Windows
    # (the child process tends to almost always return an error).
    # Apparently using "stderr=subprocess.STDOUT" fixes this pb.
    return subprocess.call(cmd, stderr=subprocess.STDOUT, shell=True)

### Implementation taken from subprocess.check_output() (available in Python
### >= 2.7 only).
def getCmdOutput(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        sys.exit("BBS>   FATAL ERROR: subprocess '%s' returned nonzero value %d\nBBS>   and generated error message:\nBBS>     %s" % (cmd, retcode, output))
    return output

def doOrDie(cmd):
    retcode = call(cmd)
    if retcode == 0:
        return
    sys.exit("BBS>   FATAL ERROR: subprocess '%s' returned nonzero value %d!" % (cmd, retcode))

if sys.platform == "win32":
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
        print "BBS>     Process properties for PID %d:" % proc.ProcessID
        for prop in proc.Properties_:
            print "BBS>     | - %s: %s" % (prop.Name, prop.Value)
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
        os.kill(pid, signal.SIGKILL)
        return
    # From Python Cookbook:
    #   http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/347462
    #win32api.TerminateProcess(int(proc._handle), -1)
    # but it doesn't work because it only kills the "cmd.exe" process
    # but not its child (the command passed in the cmd arg of Popen()).
    # Alternative to the above command (modified version of a
    # solution posted on the above web page, "/T" stands for tree
    # so it kills pid + all childs):
    #os.popen('TASKKILL /F /PID %d /T' % pid)
    # The above command proved not to be 100% reliable on gewurz either
    # (64-bit Windows Server 2008 R2 Enterprise), so let's try the
    # following:
    subprocs = listSubprocs(pid)
    if subprocs == None:
        return  # pid just vanished ==> nothing to do
    cmd = 'TASKKILL /F /PID %d /T' % pid
    retcode = subprocess.call(cmd, stderr=subprocess.STDOUT)
    print "BBS>   NOTE: %s returned code %d" % (cmd, retcode)
    all_PIDs = getAllActivePIDs()
    for proc2 in subprocs:
        pid2 = proc2.ProcessID
        if not pid2 in all_PIDs:
            continue
        print "BBS>   NOTE: %s failed to kill subprocess %d (%s)." \
              % (cmd, pid2, proc2.Name)
        printProcProperties(proc2)
        cmd2 = 'TASKKILL /F /PID %d' % pid2
        for i in range(5):
            print "BBS>     Now trying with %s ..." % cmd2,
            retcode2 = subprocess.call(cmd2, stderr=subprocess.STDOUT)
            print "(returned code %d)" % retcode2,
            if getProcByPID(pid2) == None:
                print "OK"
                break
            print "FAILED!"
            if i >= 4:
                print "BBS>     Giving up (after 5 tries)."
                break
            print "BBS>     Will try again in 10 seconds."
            sleep(10)
    return

### What if cmd is not found, can't be started or crashes?
def runJob(cmd, stdout=None, maxtime=2400.0, verbose=False):
    if verbose:
        print "BBS>   runJob(): " + cmd
    if stdout == None:
        out = None
    else:
        out = open(stdout, 'w')
    t0 = time.time()
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
        dt = time.time() - t0
        if dt > maxtime:
            timeout = True
            break
        sleep(0.1)
        nloop += 1
        if verbose and nloop % 100 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
    if verbose:
        dt = time.time() - t0
        sys.stdout.write("] = %.2f seconds / " % dt)
    if timeout:
        retcode = None
        if verbose:
            print "TIMEOUT!"
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
                print "ERROR!"
            else:
                print "OK"
    if stdout != None:
        out.close()
    return retcode

def tryHardToRunJob(cmd, nb_attempts=1, stdout=None, maxtime=60.0, sleeptime=20.0, verbose=False):
    for i in range(nb_attempts):
        retcode = runJob(cmd, stdout, maxtime, verbose)
        if retcode == 0:
            return
        sleep(sleeptime)
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sys.exit("%d failed attempts => EXIT at %s." % (nb_attempts, now))

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
        self._name = name                # the job name
        self._cmd = cmd                  # the command to execute (or None)
        self._output_file = output_file  # where to capture std out and err
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

def _unprocessedDeps(deps, processed_jobs):
    unprocessed_deps = []
    for dep in deps:
        if not dep in processed_jobs:
            unprocessed_deps.append(dep)
    return unprocessed_deps

def _getNextJobToProcess(job_queue, job_deps, processed_jobs, nb_busy_slots):
    if job_deps == None:
        job_rank = len(processed_jobs) + nb_busy_slots
        job = job_queue[job_rank]
        return job
    # Look for a job in the queue that is waiting to be processed (i.e. has
    # no '_rank' attribute) and for which all deps have already been processed.
    for job in job_queue:
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
    for job in job_queue:
        if hasattr(job, '_rank'):
            continue
        unprocessed_deps = _unprocessedDeps(job_deps[job._name], processed_jobs)
        job._unprocessed_deps = unprocessed_deps
        return job
    # Should never get here (would happen only if no more jobs in the queue
    # are waiting to be processed and 'nb_busy_slots' is 0).
    sys.exit("BBS>   FATAL ERROR in _getNextJobToProcess(): Unexpectedly reached end of function.")

def _logActionOnQueuedJob(action, job, nb_jobs, nb_slots, job_deps=None):
    print
    msg = "%s JOB %s (%d/%d)" % (action, job._name, job._rank+1, nb_jobs)
    if nb_slots != 1:
        msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
    print "bbs.jobs.processJobQueue> %s" % msg
    if job_deps != None:
        print "bbs.jobs.processJobQueue>   Deps:",
        print job_deps[job._name]
        print "bbs.jobs.processJobQueue>   Unprocessed deps:",
        print job._unprocessed_deps
    print "bbs.jobs.processJobQueue>   Command: %s" % job._cmd

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
    job._startedat = currentDateString()
    job._t0 = time.time()
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
    job._dt = time.time() - job._t0
    if job._proc.poll() == None:
        if job._dt < maxtime_per_job:
            return 0
        killProc(job._proc.pid)
        if verbose:
            if nb_slots == 1:
                print "/TIMEOUT!]"
            else:
                print
                msg = "KILL JOB %s (%d/%d)" % (job._name, job._rank+1, nb_jobs)
                msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
                msg += " after %.2f seconds" % job._dt
                print "bbs.jobs.processJobQueue> %s" % msg
        return -1
    job._retcode = job._proc.wait()
    if verbose:
        if nb_slots == 1:
            if job._retcode == 0:
                print "/OK]"
            else:
                print "/ERROR!/retcode=%d]" % job._retcode
        else:
            print
            msg = "DONE JOB %s (%d/%d)" % (job._name, job._rank+1, nb_jobs)
            msg += " ON SLOT %s/%s" % (job._slot+1, nb_slots)
            msg += " after %.2f seconds [retcode=%d]" % (job._dt, job._retcode)
            print "bbs.jobs.processJobQueue> %s" % msg
    return 1

def _logSummaryOfJobsWithUnprocessedDeps(job_queue, job_deps):
    print "bbs.jobs.processJobQueue> %s" % \
          "Jobs with unprocessed deps at time of processing:"
    i = 0
    for job in job_queue:
        unprocessed_deps = job._unprocessed_deps
        if len(unprocessed_deps) == 0:
            continue
        i += 1
        msg = "JOB %s (%d/%d)" % (job._name, job._rank+1, len(job_queue))
        print "bbs.jobs.processJobQueue>   %s" % msg
        print "bbs.jobs.processJobQueue>     Deps:",
        print job_deps[job._name]
        print "bbs.jobs.processJobQueue>     Unprocessed deps:",
        print job._unprocessed_deps
        print "bbs.jobs.processJobQueue>     Command: %s" % job._cmd
    if i != 0:
        print "bbs.jobs.processJobQueue>   Total = %d" % i
    else:
        print "bbs.jobs.processJobQueue>   %s" % None
    return

### Process the list of jobs passed in 'job_queue' in parallel.
### Will run at most 'nb_slots' jobs simultaneously.
### The 'job_queue' arg must be a list of QueuedJob objects.
### The 'job_deps' arg must be None or a dict with 1 entry per job listing the
### deps for each job i.e. which jobs must be processed before a given job can
### be processed.
def processJobQueue(job_queue, job_deps, nb_slots=1,
                    maxtime_per_job=3600.0, verbose=False):
    nb_jobs = len(job_queue)
    if verbose:
        print
        print "bbs.jobs.processJobQueue>",
        print "%d jobs in the queue. Start processing them using %d slots" % \
              (nb_jobs, nb_slots)
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
                job._endedat = currentDateString()
                cumul += job.AfterRun()
            else: # timed out
                job._endedat = currentDateString()
                job.AfterTimeout(maxtime_per_job)
            processed_jobs.append(job._name)
            slots[slot] = None
            nb_busy_slots -= 1
        # Slot 'slot' is available
        while True:
            job_rank = len(processed_jobs) + nb_busy_slots
            if job_rank == nb_jobs:
                # All the jobs are either already processed or currently being
                # processed.
                break
            job = _getNextJobToProcess(job_queue, job_deps, processed_jobs,
                                       nb_busy_slots)
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
                break
            # SKIP the job
            if verbose:
                _logActionOnQueuedJob("SKIP", job, nb_jobs, 1, job_deps)
            processed_jobs.append(job._name)
    if verbose:
        print
        print "bbs.jobs.processJobQueue> Finished."
        if job_deps != None:
            _logSummaryOfJobsWithUnprocessedDeps(job_queue, job_deps)
        print
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
    hostname = getCmdOutput('hostname')
    if hostname[-1] == '\n':
        hostname = hostname[0:-1]
    hostname = hostname.lower()
    hostname = hostname.replace(".local", "")
    hostname = hostname.replace(".fhcrc.org", "")
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

