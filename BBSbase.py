##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: July 19, 2011
###

import sys
import os
import tarfile

import bbs.fileutils
import bbs.parse
import bbs.jobs
import BBScorevars
import BBSvars


def Untar(tarball, dir=None, verbose=False):
    key = 'BBS_TAR_CMD'
    if key in os.environ and os.environ[key] != "":
        tar_cmd = os.environ[key]
        options = 'zxf'
        if verbose:
            options += 'v'
        cmd = tar_cmd + ' ' + options + ' ' + tarball
        if dir != None:
            cmd += ' -C %s' % dir
        bbs.jobs.doOrDie(cmd)
    else:
        ## This method doesn't restore the file permissions on Windows!
        if dir != None:
            sys.exit("ERROR in Untar(): dir != None is not supported")
        tar = tarfile.open(tarball, mode="r:gz")
        for tarinfo in tar:
            tar.extract(tarinfo)
        tar.close()
    return

# The script passed thru Rscript must NOT contain spaces or it will break
# on Windows!
def Rscript2syscmd(Rscript, Roptions=None):
    if sys.platform == "win32":
        syscmd = 'echo %s | %s --slave' % (Rscript, BBSvars.r_cmd)
    else:
        syscmd = 'echo "%s" | %s --slave' % (Rscript, BBSvars.r_cmd)
    if Roptions != None:
        syscmd += ' ' + Roptions
    return syscmd


##############################################################################
### Generate the system commands used for installing (STAGE2), building
### (STAGE3 and STAGE5), and checking (STAGE4) each package.
##############################################################################

def _BiocGreaterThanOrEqualTo(x, y):
    bioc_version = BBScorevars.getenv('BBS_BIOC_VERSION', False)
    # If BBS_BIOC_VERSION is not defined, then we assume it's the latest version.
    if bioc_version == None:
        return True
    parts = bioc_version.split('.')
    x0 = int(parts[0])
    y0 = int(parts[1])
    return x0 > x or (x0 == x and y0 >= y)

def _getPkgFieldFromMeatIndex(pkg, field):
    Central_rdir = BBScorevars.Central_rdir
    dcf = Central_rdir.WOpen(BBScorevars.meat_index_file)
    val = bbs.parse.getPkgFieldFromDCF(dcf, pkg, field,
                                       BBScorevars.meat_index_file)
    dcf.close()
    return val.replace(" ", "").split(",")

def _noExampleArchs(pkg):
    no_examples = _getPkgFieldFromMeatIndex(pkg, 'NoExamplesOnPlatforms')
    clean = []
    for item in no_examples:
        clean.append(item.strip())
    no_examples = clean
    archs = []
    if "mac" in no_examples:
        archs.append("darwin")
    if "win" in no_examples:
        archs.append("win32")
        archs.append("win32")
    if "win32" in no_examples:
        archs.append("win32")
    if "win64" in no_examples:
        archs.append("win32")
    if "linux2" in no_examples:
        archs.append("linux2")
# see
#http://stackoverflow.com/questions/2144748/is-it-safe-to-use-sys-platform-win32-check-on-64-bit-python
# to explain the above.
    return archs

def _supportedWinArchs(pkg):
    unsupported = _getPkgFieldFromMeatIndex(pkg, 'UnsupportedPlatforms')
    archs = []
    if "win" in unsupported:
        return archs
    if "win32" not in unsupported:
        archs.append("i386")
    if "win64" not in unsupported:
        archs.append("x64")
    return archs

### 'pkgdir_path' must be a path to a package source tree.
def _get_RCMDbuild_cmd(pkgdir_path):
    arch = ""
    if sys.platform == "win32":
        win_archs = _supportedWinArchs(pkgdir_path)
        if len(win_archs) == 1:
            arch = " --arch %s" % win_archs[0]
    cmd = '%s%s CMD build' % (BBSvars.r_cmd, arch)
    if sys.platform == "win32":
        ## Fix the permissions on Windows only.
        ## The real purpose of this is to try to work around a strange Cygwin
        ## tar problem ("file changed as we read it") observed so far on
        ## Windows Server 2008 R2 Enterprise (64-bit) only.
        ## Traversing the package source tree, with e.g. a call to
        ## 'chmod a+r pkgdir_path -R', just before we try to build the
        ## package seems to "fix" the state of the filesystem and to
        ## make 'tar' work again on it.
        cmd = 'chmod a+r ' + pkgdir_path + ' -R && ' + cmd
    common_opts = ["--keep-empty-dirs", "--no-resave-data"]
    if BBScorevars.subbuilds == "bioc-longtests":
        common_opts += ["--no-build-vignettes", "--no-manual"]
    cmd = "%s %s" % (cmd, ' '.join(common_opts))
    return cmd

### 'srcpkg_path' must be a path to a package source tarball.
def _getSTAGE5cmd(srcpkg_path, mode, stage):
    pkg = bbs.parse.getPkgFromPath(srcpkg_path)
    instpkg_dir = "%s.buildbin-libdir" % pkg
    rcheck_dir = "%s.Rcheck" % pkg
    if stage == 4:
        cmd = 'rm -rf %s %s && mkdir %s %s && ' % (instpkg_dir, rcheck_dir,
            instpkg_dir, rcheck_dir)
    else:
        cmd = 'rm -rf %s && mkdir %s && ' % (instpkg_dir, instpkg_dir)
    if sys.platform == 'darwin':
        cmd += '%s/utils/build-universal.sh %s %s %s' % \
            (BBScorevars.BBS_home, srcpkg_path, BBSvars.r_cmd, instpkg_dir)
        return cmd
    if mode != "multiarch":
        cmd += '%s CMD INSTALL --build --no-multiarch --library=%s %s' % \
               (BBSvars.r_cmd, instpkg_dir, srcpkg_path)
        return cmd
    if not _BiocGreaterThanOrEqualTo(2, 7):
        sys.exit("no multiarch capabilities for 'R CMD INSTALL' before BioC 2.7 / R 2.12")
    if sys.platform != "win32":
        sys.exit("BBS supports multiarch STAGE5 only on Windows for now!")
    win_archs = _supportedWinArchs(pkg)
    if len(win_archs) == 0:
        return None
    if len(win_archs) == 1:
        middle = '--arch %s CMD INSTALL --build --no-multiarch' % win_archs[0]
    else:
        if stage == 5:
            version = bbs.parse.getVersionFromPath(srcpkg_path)
            #cmd = "cd %s.Rcheck/%s && zip -r ../../%s_%s.zip . & cd ../.." % (
            #    pkg, pkg, pkg, version)
            cmd = "cd %s.buildbin-libdir/%s && zip -r ../../%s_%s.zip ." % \
                  (pkg, pkg, pkg, version) + " & cd ../.."
            return cmd
        elif stage == 4:
            middle = 'CMD INSTALL --build --merge-multiarch'
    cmd += '%s %s --library=%s %s' % \
           (BBSvars.r_cmd, middle, instpkg_dir, srcpkg_path)
    return cmd

### During STAGE1, we need to build a "light" source tarball for each package.
### By "light" here we mean that we don't care about the vignette or \Sexpr
### directives in the man pages: trying to execute the code contained in the
### vignette and/or the \Sexpr directives is too expensive (it can take a long
### time) and, most importantly, it's too risky (it can fail).
### Using 'R CMD build --no-vignettes' for building a "light" source tarball
### isn't good enough: it will still try to install the package if the man
### pages contain \Sexpr directives. Unfortunately, at this time (R 2.14),
### there doesn't seem to be any option for turning off the evaluation of the
### \Sexpr. So, for now, we build the "light" source tarball "by hand" i.e.
### we just use 'tar zcf'.
def getSTAGE1cmd(pkgdir_path):
    #cmd = _get_RCMDbuild_cmd(pkgdir_path) + ' --no-build-vignettes ' + pkgdir_path
    key = 'BBS_TAR_CMD'
    tar_cmd = os.environ[key]
    srcpkg_file = bbs.parse.getSrcPkgFileFromDir(pkgdir_path)
    cmd = '%s zcf %s %s' % (tar_cmd, srcpkg_file, pkgdir_path)
    return cmd

def _mustRunSTAGE2InMultiarchMode():
    return BBScorevars.subbuilds == "bioc" and \
           "BBS_STAGE2_MODE" in os.environ and \
           os.environ['BBS_STAGE2_MODE'] == 'multiarch'

def getSTAGE2cmdForNonTargetPkg(pkg):
    script_path = os.path.join(BBScorevars.BBS_home,
                               "utils",
                               "installNonTargetPkg.R")
    # Backslahes in the path injected in the R scripts will be seen as escape
    # characters by R so we need to replace them. Nothing will be replaced
    # on a Unix-like platform, only on Windows where the paths can actually
    # contain backslahes.
    script_path = script_path.replace('\\', '/')
    Rscript = "source('%s');" % script_path
    if sys.platform == "win32" and _mustRunSTAGE2InMultiarchMode():
        Rscript += "installNonTargetPkg('%s',multiArch=TRUE)" % pkg
    else:
        Rscript += "installNonTargetPkg('%s')" % pkg
    return Rscript2syscmd(Rscript)

def getSTAGE2cmd(pkg, version):
    cmd = '%s CMD INSTALL %s' % (BBSvars.r_cmd, pkg)
    prepend = bbs.parse.getBBSoptionFromDir(pkg, 'RbuildPrepend')
    if sys.platform == "win32":
        prepend_win = bbs.parse.getBBSoptionFromDir(pkg, 'RbuildPrepend.win')
        if prepend_win != None:
            prepend = prepend_win
        win_archs = _supportedWinArchs(pkg)
        if _mustRunSTAGE2InMultiarchMode() and len(win_archs) == 2:
            curl_cmd = BBScorevars.getenv('BBS_CURL_CMD')
            srcpkg_file = pkg + '_' + version + '.tar.gz'
            srcpkg_url = BBScorevars.Central_rdir.url + '/src/contrib/' + \
                         srcpkg_file
            zipfile = srcpkg_file.replace(".tar.gz", ".zip")
            cmd = 'rm -rf %s.buildbin-libdir' % pkg + ' && ' + \
                  'mkdir %s.buildbin-libdir ' % pkg + ' && ' + \
                  '%s -O %s' % (curl_cmd, srcpkg_url) + ' && ' + \
                  '%s CMD INSTALL --build --library=%s.buildbin-libdir --merge-multiarch %s' % \
                  (BBSvars.r_cmd, pkg, srcpkg_file) + ' && ' + \
                  '%s CMD INSTALL %s ' % (BBSvars.r_cmd,
                    zipfile)  + ' && ' + \
                  'rm %s %s' % (srcpkg_file, zipfile)
        else:
            cmd = '%s --arch %s CMD INSTALL --no-multiarch %s' % \
                  (BBSvars.r_cmd, win_archs[0], pkg)
    if prepend != None:
        cmd = '%s %s' % (prepend, cmd)
    return cmd

def getSTAGE3cmd(pkgdir_path):
    return _get_RCMDbuild_cmd(pkgdir_path) + ' ' + pkgdir_path

### 'srcpkg_path' must be a path to a package source tarball.
def getSTAGE4cmd(srcpkg_path):
    pkg = bbs.parse.getPkgFromPath(srcpkg_path)
    cmd = ''
    prepend = bbs.parse.getBBSoptionFromDir(pkg, 'RcheckPrepend')
    if sys.platform == "win32":
        prepend_win = bbs.parse.getBBSoptionFromDir(pkg, 'RcheckPrepend.win')
        if prepend_win != None:
            prepend = prepend_win
    if prepend != None:
	cmd = '%s %s' % (prepend, cmd)
    if BBScorevars.subbuilds == "bioc-longtests":
        common_opts = ["--test-dir=longtests",
                       "--no-stop-on-test-error",
                       "--no-codoc",
                       "--no-examples",
                       "--no-manual",
                       "--ignore-vignettes",
                       "--check-subdirs=no"]
    else:
        common_opts = ["--no-vignettes", "--timings"]
        ## Note that 64-bit machines gewurz and moscato1 give a value of
        ## 'win32' for sys.platform. This means that _noExampleArchs() may
        ## not be returning useful results if the intent is to not run
        ## examples for a particular Windows sub-architecture.
        no_example_archs = _noExampleArchs(pkg)
        if sys.platform in no_example_archs:
            common_opts += ["--no-examples"]
    common_opts = ' '.join(common_opts)
    if BBSvars.STAGE4_mode != "multiarch":
        cmd += '%s CMD check %s' % (BBSvars.r_cmd, common_opts)
        ## Starting with R-2.12, 'R CMD check' on Windows and Mac OS X can do
        ## runtime tests on various installed sub-archs. New options have been
        ## added to provide some control on this (see 'R CMD check -h').
        ## In particular:
        ##   --multiarch       do runtime tests on all installed sub-archs
        ##   --no-multiarch    do runtime tests only on the main
        ##                     sub-architecture
        ##   --force-multiarch run tests on all sub-archs even for packages
        ##                     with no compiled code
        ## Problems:
        ##   - The default (--multiarch) won't do runtime tests on all
        ##     sub-archs if the package has no native code. So for example a
        ##     package like AnnotationDbi can show up green on the build report
        ##     even though it wouldn't load for 'arch=ppc' because RSQLite is
        ##     not installed for this arch. Then a package like Biostrings or
        ##     XDE that depends on AnnotationDbi will show up red on the build
        ##     report because it *does* have native code (and no configure
        ##     script) so 'R CMD check' will actually try to load it for
        ##     'arch=ppc'... and will fail!
        ##     One way to avoid this problem would be to install all the
        ##     packages with native code for all sub-archs but AFAIK
        ##     'R CMD INSTALL' (and consequently install.packages()) still
        ##     doesn't allow this for packages with a configure script.
        ##   - Using --force-multiarch would help produce more consistent check
        ##     results by having AnnotationDbi show up red too but we would
        ##     still have the issue that there is no easy way to get RSQLite
        ##     installed for all sub-archs. Anyway, --force-multiarch is not
        ##     even an option right now because: (1) it's broken on packages
        ##     with a configure script, and (2) it would put so much load on
        ##     our Mac OS X build machine (pelham) that a build run would
        ##     probably take more than 12h.
        ##   - So for now (Sep 9, 2010) we just turn off multiarch runtime
        ##     testing.
        ##   - UPDATE: May 10, 2011 - Explicitely turning off multiarch runtime
        ##     testing on Windows too.
        ##   - UPDATE: March 18, 2015: Packages are now only built on a single
        ##     architecture for Mac (x86_64), so --no-multiarch has no effect.
        ##     removing it from Mac builds.
        if sys.platform == "win32" and _BiocGreaterThanOrEqualTo(2, 7):
            cmd += ' --no-multiarch'
        return cmd + ' ' + srcpkg_path
    if not _BiocGreaterThanOrEqualTo(2, 7):
        sys.exit("no multiarch capabilities for 'R CMD check' before BioC 2.7 / R 2.12")
    if sys.platform != "win32":
        sys.exit("BBS supports multiarch STAGE4 only on Windows for now!")
    win_archs = _supportedWinArchs(pkg)
    if len(win_archs) == 0:
        return None
    if len(win_archs) == 1:
        middle = '--arch %s CMD check --no-multiarch' % win_archs[0]
        cmd += '%s %s %s %s' % (BBSvars.r_cmd, middle, common_opts, srcpkg_path)
        return cmd
    ## For some rare BioC packages (e.g. Rdisop, fabia, bgx -- as of July
    ## 2011), 'R CMD check --force-multiarch' will fail to do a bi-arch
    ## install. My first attempt to work around this was to use
    ## 'R CMD check --force-multiarch --install-args="--merge-multiarch"'
    ## but, unfortunately, this didn't work ('R CMD check' tries to install
    ## the *extracted* tarball but the --merge-multiarch option only works
    ## on a tarball).
    ## Thanks to Uwe Ligges for suggesting the following workaround:
    ##   https://stat.ethz.ch/pipermail/r-devel/2011-June/061377.html
    ## Step 1: Installation:
    instout_file = '%s-install.out' % pkg
    rcheck_dir = "%s.Rcheck" % pkg
    instout_file_rcheck = os.path.join(rcheck_dir, "00install.out")
    cmd1 = '%s >%s 2>&1 && cp %s %s ' % \
           (_getSTAGE5cmd(srcpkg_path, "multiarch", 4), instout_file_rcheck,
            instout_file_rcheck, instout_file)
    ## Step 2: Check (without installation, since that happened before
    ## already, using the install log from step 1):
    instpkg_dir = "%s.buildbin-libdir" % pkg
    middle = 'CMD check --library=%s --install="check:%s" --force-multiarch' % \
             (instpkg_dir, instout_file)
    cmd2 = '%s %s %s %s %s' % (cmd, BBSvars.r_cmd, middle, common_opts, srcpkg_path)
    ## Step 3: Move installed stuff to <pkg>.Rcheck/
    #cmd3 = 'mv %s/* %s.Rcheck/' % (instpkg_dir, pkg)
    ## Step 4: Cleanup
    #cmd4 = 'rmdir %s' % instpkg_dir
    #return '%s && %s && %s && %s' % (cmd1, cmd2, cmd3, cmd4)
    return '%s && %s' % (cmd1, cmd2)

def getSTAGE5cmd(srcpkg_path):
    return _getSTAGE5cmd(srcpkg_path, BBSvars.STAGE5_mode, 5)


##############################################################################
### Output files produced by 'R CMD build/check'.
##############################################################################

class PkgDumps:
    def __init__(self, product_path, prefix):
        self.product_path = product_path
        self.out_file = prefix + '-out.txt'
        self.MISSING_file = prefix + '-MISSING'
        self.summary_file = prefix + '-summary.dcf'
    def IsComplete(self, verbose=False):
        OK = (self.product_path == None or os.path.exists(self.product_path)) \
             and os.path.exists(self.out_file) \
             and os.path.exists(self.summary_file)
        if verbose and OK:
            print "BBS>   Found output files",
        return OK
    def Push(self, rdir):
        if self.product_path == None:
            to_push = []
        else:
            if os.path.exists(self.product_path):
                if os.path.exists(self.MISSING_file):
                    os.remove(self.MISSING_file)
                to_push = [self.product_path]
            else:
                bbs.fileutils.touch(self.MISSING_file)
                to_push = [self.MISSING_file]
        to_push += [self.out_file, self.summary_file]
        rdir.Mput(to_push, False, True)
        return


##############################################################################
### The Summary class is used by the _MakeSummary() method of the BuildPkg_Job
### and CheckSrc_Job classes to generate a summary.
##############################################################################

### Finally, I opted for the Append() solution to add extra stuff to the
### summary (and not for the "derive the Summary class and overwrite the
### Write() method" solution).
class Summary:
    def __init__(self, pkg, version, cmd):
        self.pkg = pkg
        self.version = version
        self.cmd = cmd
        self.tail = []
    def Append(self, field, val):
        pair = (field, val)
        self.tail.append(pair)
    def Write(self, file):
        f = open(file, 'w')
        f.write('Package: %s\n' % self.pkg)
        f.write('Version: %s\n' % self.version)
        f.write('Command: %s\n' % self.cmd)
        f.write('StartedAt: %s\n' % self.startedat)
        f.write('EndedAt: %s\n' % self.endedat)
        f.write('EllapsedTime: %.1f seconds\n' % self.dt)
        if self.retcode == None:
            f.write('RetCode: None\n')
        else:
            f.write('RetCode: %d\n' % self.retcode)
        f.write('Status: %s\n' % self.status)
        for pair in self.tail:
            f.write('%s: %s\n' % pair)
        f.close()
        return


##############################################################################
### CORE FUNCTIONS: Called by the STAGE<N>_loop() functions (N=2,3,4,5).
##############################################################################

class InstallPkg_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, rdir):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        if pkgdumps != None:
            self._output_file = pkgdumps.out_file
        else:
            self._output_file = None
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.rdir = rdir
        self.summary = Summary(pkg, version, cmd)
    def RerunMe(self):
        locking_pkg = bbs.parse.extractLockingPackage(self._output_file)
        ## We re-run only if the lock was on one of the deps, but not on the
        ## package itself.
        rerun_me = locking_pkg != None and locking_pkg != self.pkg
        return rerun_me
    def _MakeSummary(self):
        self.summary.startedat = self._startedat
        self.summary.endedat = self._endedat
        self.summary.dt = self._dt
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.rdir)
    def AfterRun(self):
        self.summary.retcode = self._retcode
        if self._retcode == 0 and \
           bbs.parse.installPkgWasOK(self._output_file, self.pkg):
            self.summary.status = 'OK'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()

class BuildPkg_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, rdir):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        self._output_file = pkgdumps.out_file
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.rdir = rdir
        self.summary = Summary(pkg, version, cmd)
    def _MakeSummary(self):
        self.summary.startedat = self._startedat
        self.summary.endedat = self._endedat
        self.summary.dt = self._dt
        pkg_file = self.pkgdumps.product_path
        if os.path.exists(pkg_file):
            pkg_file_size = bbs.fileutils.human_readable_size(bbs.fileutils.total_size(pkg_file), True)
        else:
            pkg_file = 'None'
            pkg_file_size = 'NA'
        self.summary.Append('PackageFile', pkg_file)
        self.summary.Append('PackageFileSize', pkg_file_size)
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.rdir)
    def AfterRun(self):
        # Avoid leaving rogue processes messing around on the build machine.
        # self._proc.pid should be already dead but some of its children might
        # still be alive. They need to die too. bbs.jobs.killProc() should work
        # on a non-existing pid and it should be able to kill all the processes
        # that were started directly or indirectly by pid.
        # This needs to happen before calling self._MakeSummary() because
        # these rogue processes can break the rsync command used by
        # self.pkgdumps.Push(self.rdir) above by holding on some of the files
        # that need to be pushed to the central build node.
        bbs.jobs.killProc(self._proc.pid)
        self.summary.retcode = self._retcode
        pkg_file = self.pkgdumps.product_path
        if os.path.exists(pkg_file) and self._retcode == 0:
            self.summary.status = 'OK'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()

class CheckSrc_Job(bbs.jobs.QueuedJob):
    def __init__(self, pkg, version, cmd, pkgdumps, rdir):
        ## Required fields
        self._name = pkg
        self._cmd = cmd
        self._output_file = pkgdumps.out_file
        ## Additional fields
        self.pkg = pkg
        self.version = version
        self.pkgdumps = pkgdumps
        self.rdir = rdir
        self.summary = Summary(pkg, version, cmd)
        self.warnings = 'NA'
        #NOT NEEDED. '00install.out' is under the '<pkg>.Rcheck' dir
        #and we already push this dir to self.rdir as part of self.pkgdumps
        #self.install_out = os.path.join('%s.Rcheck' % pkg, '00install.out')
    def _MakeSummary(self):
        self.summary.startedat = self._startedat
        self.summary.endedat = self._endedat
        self.summary.dt = self._dt
        check_dir = self.pkgdumps.product_path
        if os.path.exists(check_dir):
            # Before we push the .Rcheck/ folder to the central node, we
            # remove 2 subfolders from it (that are not needed downstream):
            #   1) the .Rcheck/00_pkg_src/ folder (contains a copy of the
            #      package source tree);
            #   2) the .Rcheck/<pkg>/ folder (contains the installed package).
            # This can significantly reduce the size of the .Rcheck/ folder,
            # especially for data experiment packages. It also reduces disk
            # usage on both, the local node and the central node.
            pkg_src_tree = os.path.join(check_dir, "00_pkg_src")
            if os.path.exists(pkg_src_tree):
                bbs.fileutils.nuke_tree(pkg_src_tree)
            pkg_install_dir = os.path.join(check_dir, self.pkg)
            if os.path.exists(pkg_install_dir):
                bbs.fileutils.nuke_tree(pkg_install_dir)
        else:
            check_dir = 'None'
        self.summary.Append('CheckDir', check_dir)
        self.summary.Append('Warnings', self.warnings)
        self.summary.Write(self.pkgdumps.summary_file)
        self.pkgdumps.Push(self.rdir)
        ## Sometimes, '00install.out' is not generated (e.g. when some required
        ## packages are not available)
	#NOT NEEDED (see above).
        #if os.path.exists(self.install_out):
        #    self.rdir.Put(self.install_out, True, True)
    def AfterRun(self):
        # Avoid leaving rogue processes messing around on the build machine.
        # self._proc.pid should be already dead but some of its children might
        # still be alive. They need to die too. bbs.jobs.killProc() should work
        # on a non-existing pid and it should be able to kill all the processes
        # that were started directly or indirectly by pid.
        # This needs to happen before calling self._MakeSummary() because
        # these rogue processes can break the rsync command used by
        # self.pkgdumps.Push(self.rdir) above by holding on some of the files
        # that need to be pushed to the central build node.
        bbs.jobs.killProc(self._proc.pid)
        self.summary.retcode = self._retcode
        if self._retcode == 0:
            self.warnings = bbs.parse.countWARNINGs(self._output_file)
            if self.warnings == "0":
                self.summary.status = 'OK'
            else:
                self.summary.status = 'WARNINGS'
            cumul_inc = 1
        else:
            self.summary.status = 'ERROR'
            cumul_inc = 0
        self._MakeSummary()
        return cumul_inc
    def AfterTimeout(self, maxtime_per_job):
        self.summary.retcode = None
        self.summary.status = 'TIMEOUT'
        self._MakeSummary()
