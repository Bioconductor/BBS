#!/usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: June 22, 2011
###
###
###
### rdir module
###

import sys
import os
### urllib.urlopen() doesn't raise an error when the object is not found (HTTP
### Error 404) but urllib2.urlopen() does (raises an urllib2.HTTPError object)
import urllib2

import fileutils
import jobs


### Expected bandwidth (in kilobits/s) for transferring data back and forth
### between the central and the secondary build nodes.
### Notes:
###   - This is used for triggering timeouts so in doubt estimate low.
###   - Right now it's only used for transferring data back from the secondary
###     nodes to the central node.
bandwidth_in_kbps = 800.0  # 100 kilobytes per sec
bandwidth_in_bytes_per_sec = bandwidth_in_kbps * 1000.0 / 8.0

class RemoteDir:

    # When passed None to the 'host' arg, then degrades to a local dir (and
    # then the 'ssh_cmd' arg. is ignored).
    # When passed None to the 'path' arg, then degrades to a web-based only
    # remote dir (located at the URL specified by 'url'). In that case all
    # the remaining args are ignored and the remote dir can only be accessed
    # in read-only mode (via the WOpen method).
    def __init__(self, label, url, path, host, user, ssh_cmd, rsync_cmd, rsync_rsh_cmd):
        self.label = label
        self.url = url
        self.path = path
        self.host = host
        self.user = user
        self.ssh_cmd = ssh_cmd
        self.rsync_cmd = rsync_cmd
        self.rsync_rsh_cmd = rsync_rsh_cmd

    def subdir(self, subdir):
        url = self.url
        if url != None:
            url += '/' + subdir
        path = self.path
        if path != None:
            path += '/' + subdir
        return RemoteDir(self.label + '/' + subdir,
                         url, path,
                         self.host, self.user,
                         self.ssh_cmd, self.rsync_cmd, self.rsync_rsh_cmd)

    def WOpen(self, file, catch_HTTPerrors=False):
        file_url = self.url + '/' + file
        if not catch_HTTPerrors:
            return urllib2.urlopen(file_url)
        try:
            f = urllib2.urlopen(file_url)
        except urllib2.HTTPError:
            return None
        return f

    def get_full_remote_path(self):
        if self.host == None:
            # self is a local dir
            return self.path
        # self is a remote dir
        if self.user == None:
            return "%s:%s" % (self.host, self.path)
        return "%s@%s:%s" % (self.user, self.host, self.path)

    # 'src_path' is relative to 'self'
    # 'dest_path' is a local path that can be absolute or relative to the
    # current dir
    def Get(self, src_path, dest_path=".", verbose=False):
        if self.path == None:
            # 'self' is a web-based only remote dir. 'src_path' must be
            # pointing to a remote file accessible thru HTTP. 'dest_path'
            # must be pointing to a local folder into which the remote file
            # will be downloaded (replacing any existing file).
            src_file = self.WOpen(src_path)
            dest_path = os.path.join(dest_path, src_path)
            dest_file = open(dest_path, 'w')
            for line in src_file:
                dest_file.write(line)
            dest_file.close()
            src_file.close()
            return
        if self.host == None:
            # self is a local dir
            src_path = "%s/%s" % (self.path, src_path)
            cmd = "%s %s %s" % (self.rsync_cmd, src_path, dest_path)
        else:
            # self is a remote dir
            src_path = "%s/%s" % (self.get_full_remote_path(), src_path)
            cmd = "%s %s %s" % (self.rsync_rsh_cmd, src_path, dest_path)
        jobs.tryHardToRunJob(cmd, 5, None, 60.0, 20.0, True, verbose)
        return

    def _Call(self, remote_cmd):
        if self.host != None:
            # self is a remote dir => remote execution
            if self.user != None:
                cmd = self.ssh_cmd + " " + self.user + "@" + self.host + " '" + remote_cmd + "'"
            else:
                cmd = self.ssh_cmd + " " + self.host + " '" + remote_cmd + "'"
        else:
            # self is a local dir => local execution
            cmd = remote_cmd
        return jobs.call(cmd)

    def MakeMe(self, verbose=False):
        if verbose:
            print "BBS>   mkdir %s/..." % self.label,
        remote_cmd = 'mkdir -p ' + self.path
        retcode = self._Call(remote_cmd)
        if retcode != 0:
            if not verbose:
                print "BBS>   mkdir %s/..." % self.label,
            sys.exit("ERROR! (retcode: %d)" % retcode)
        if verbose:
            print "OK"
        return

    def RemoveMe(self, verbose=False):
        if verbose:
            print "BBS>   rm -rf %s/..." % self.label,
        remote_cmd = 'rm -rf ' + self.path
        retcode = self._Call(remote_cmd)
        if retcode != 0:
            if not verbose:
                print "BBS>   rm -rf %s/..." % self.label,
            sys.exit("ERROR! (retcode: %d)" % retcode)
        if verbose:
            print "OK"
        return

    def RemakeMe(self, verbose=False):
        if verbose:
            print "BBS>   (Re)make %s/..." % self.label,
        self.RemoveMe()
        self.MakeMe()
        if verbose:
            print "OK"
        return

    def Call(self, remote_cmd):
        remote_cmd = 'cd ' + self.path + ' && (' + remote_cmd + ')'
        return self._Call(remote_cmd)

    def List(self):
        remote_cmd = 'ls'
        # IMPLEMENT ME
        sys.exit("IMPLEMENT ME")
        rdir_files = []
        return rdir_files

    def Del(self, path, verbose=False):
        if verbose:
            print "BBS>   Delete %s/%s..." % (self.label, path),
        remote_cmd = 'rm -rf ' + path
        retcode = self.Call(remote_cmd)
        if retcode != 0:
            if not verbose:
                print "BBS>   Delete %s/%s..." % (self.label, path),
            sys.exit("ERROR! (retcode: %d)" % retcode)
        if verbose:
            print "OK"
        return

    # 'src_path' is a local path that can be absolute or relative to the
    # current dir
    def Put(self, src_path, failure_is_fatal=True, verbose=False):
        if sys.platform == "win32" and os.path.exists(src_path) and os.path.isfile(src_path):
            #os.chmod(src_path, 0644) # This doesn't work
            ## This works better but requires Cygwin.
            cmd = "chmod +r " + src_path
            jobs.runJob(cmd, None, 60.0, verbose)
        if self.host == None:
            # self is a local dir
            cmd = "%s %s %s" % (self.rsync_cmd, src_path, self.path)
        else:
            # self is a remote dir
            cmd = "%s %s %s" % (self.rsync_rsh_cmd, src_path, self.get_full_remote_path())
        maxtime = 120.0 + fileutils.total_size(src_path) / bandwidth_in_bytes_per_sec
        if verbose:
            if self.host != None:
                action = "Putting"
            else:
                action = "Copying"
            print "BBS>   %s %s in %s/:" % (action, src_path, self.label)
        jobs.tryHardToRunJob(cmd, 5, None, maxtime, 30.0, failure_is_fatal, verbose)
        return

    def Mput(self, paths, failure_is_fatal=True, verbose=False):
        for path in paths:
            self.Put(path, failure_is_fatal, verbose)
        return

    def syncLocalDir(self, local_dir, verbose=False):
        if os.path.exists(local_dir):
            if not os.path.isdir(local_dir):
                sys.exit("'%s' already exists and is not a directory => EXIT." % local_dir)
        else:
            os.mkdir(local_dir)
        oldcwd = os.getcwd()
        os.chdir(local_dir)
        if self.host == None:
            # self is a local dir too
            cmd = "%s -rlptz %s/ %s" % (self.rsync_cmd, self.path, '.')
        else:
            # self is a remote dir
            cmd = "%s -rlptz %s/ %s" % (self.rsync_rsh_cmd, self.get_full_remote_path(), '.')
        if verbose:
            print "BBS>   Syncing local '%s' with %s" % (local_dir, self.label)
        jobs.tryHardToRunJob(cmd, 3, None, 1800.0, 60.0, True, verbose)
        ## Workaround a strange problem observed so far on Windows Server
        ## 2008 R2 Enterprise (64-bit) only. After running rsync (from Cygwin)
        ## on this machine to sync a local folder, the local filesystem seems
        ## to be left in a state that confuses the 'tar' command (from Cygwin
        ## or Rtools) i.e. 'tar zcvf ...' fails when trying to store all or
        ## part of the local folder into a tarball complaining that for some
        ## subfolders "file changed as we read it".
        ## Traversing the entire local folder, with e.g. a call to
        ## 'chmod a+r . -R', seems to "fix" the state of the filesystem and
        ## to make 'tar' work again on it.
        if sys.platform == "win32":
            cmd = "chmod a+r . -R"  # from Cygwin (or Rtools)
            jobs.runJob(cmd, None, 300.0, verbose)
        os.chdir(oldcwd)
        return

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

