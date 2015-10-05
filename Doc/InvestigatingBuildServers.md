As mentioned in [DailyTasks.m](DailyTasks.md), sometimes you'll need to investigate an issue on one of the build 
servers.  To do this, see the 
[Investigating](https://github.com/Bioconductor/BBS/blob/master/README.md#investigating) section of the 
README and also consider the following.  Each build machine has a collection of log files which contain information
about it's current state.  One the Unix-like machines, you'll find these files in the directory: 
`/home/biocbuild/bbs-3.2-bioc/log`<sup>1</sup>.

To view these log files, ssh to the server you want to investigate: 

```
ssh ubuntu@linux1.bioconductor.org
```

Next, switch to the `biocbuild` user:

```
ubuntu@linux1:~$ sudo su - biocbuild
```

From there, navigate to the `/home/biocbuild/bbs-3.2-bioc/log` directory, which contains useful information about 
each build server: 

```
biocbuild@linux1:-~$ cd /home/biocbuild/bbs-3.2-bioc/log
biocbuild@linux1:-~/bbs-3.2-bioc/log$ ls -l
total 370352
-rw-rw-r-- 1 biocbuild biocbuild      4036 Oct  5 13:30 compute_coverage.log
-rw-rw-r-- 1 biocbuild biocbuild    171296 Oct  4 13:10 killproc.log
-rw-rw-r-- 1 biocbuild biocbuild 373289381 Oct  5 13:11 linux1.bioconductor.org.log
-rw-rw-r-- 1 biocbuild biocbuild   5758925 Oct  5 09:05 virtual-X.out
```

The file with the most infomration is very large and will be named like \<hostname\>.log.  Above, notice the file 
is `linux1.bioconductor.org.log`.  The best way to read this file is reading it via `tail`, to isolate the end of
the file.  For example, the following will show the last 400 lines of the file : 
```
biocbuild@linux1:-~/bbs-3.2-bioc/log$ tail -n 400 linux1.bioconductor.org.log |less
```

<hr/>
<sub>
1) Where can we find these files on Windows?  We need to describe an access process for accessing these file
from the Internet (e.g. using an ssh tunnel, or VPN).  Also, what is the exact path and user who owns the files?
</sub>
