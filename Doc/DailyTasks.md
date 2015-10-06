Each morning, the build system must be inspected (manually<sup>1</sup>).  The expected results of the nigthly build are described below.  To begin, ssh to the Linux build box : 

```
ssh ubuntu@linux1.bioconductor.org
```

Next, switch to the `biocbuild` user:

```
ubuntu@linux1:~$ sudo su - biocbuild
```

From there, navigate to the `nodes` directory, which contains useful information about each build server: 
```
cd /home/biocbuild/public_html/BBS/3.2/bioc/nodes
```
Note the current time ...
```
biocbuild@linux1:-~/public_html/BBS/3.2/bioc/nodes$ date
Mon Oct  5 12:32:47 EDT 2015
```
... and compare that against the timestamps of directories and files related to the build : 
```
biocbuild@linux1:-~/public_html/BBS/3.2/bioc/nodes$ ls -l *
linux1.bioconductor.org:
total 368
-rw-rw-r--    1 biocbuild biocbuild    458 Oct  5 09:05 BBS_EndOfRun.txt
drwxrwxr-x    2 biocbuild biocbuild 172032 Oct  5 00:45 buildsrc
drwxrwxr-x 1077 biocbuild biocbuild 147456 Oct  5 09:05 checksrc
drwxrwxr-x    2 biocbuild biocbuild  36864 Oct  4 20:21 install
drwxr-xr-x    2 biocbuild biocbuild   4096 Oct  4 20:21 NodeInfo

oaxaca:
# Output omitted for brevity

perceval:
total 428
drwxrwxr-x    2 biocbuild biocbuild  73728 Oct  5 12:33 buildbin
drwxrwxr-x    2 biocbuild biocbuild 167936 Oct  5 02:01 buildsrc
drwxrwxr-x 1055 biocbuild biocbuild 143360 Oct  5 11:40 checksrc
drwxrwxr-x    2 biocbuild biocbuild  36864 Oct  4 20:26 install
drwxr-xr-x    2 biocbuild biocbuild   4096 Oct  4 20:27 NodeInfo

windows1.bioconductor.org:
# Output omitted for brevity

```
Notice, there is a directory for each build box (linux1.bioconductor.org,  oaxaca,  perceval,  windows1.bioconductor.org).  Inside, there are various sub-directories and files.  We expect that these directories and files will be updated each day.

When the build has completely finished on a given build box, a `BBS_EndOfRun.txt` file will be created.  Notice, above there is one for the linux1.bioconductor.org server.  It is often after 1p.m. (Eastern) that the build on perceval is complete<sup>3</sup>, however Linux, Windows and the other Mac build server (oaxaca) are often finished by 11a.m. (Eastern).

To determine which nodes are finished, execute the following command: 
```
find /home/biocbuild/public_html/BBS/3.2/bioc/nodes -maxdepth 2 -type f -name "BBS_EndOfRun.txt" -exec ls -1 {} \;
```
Which will result in output like : 
```
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/windows1.bioconductor.org/BBS_EndOfRun.txt
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/linux1.bioconductor.org/BBS_EndOfRun.txt
/home/biocbuild/public_html/BBS/3.2/bioc/nodes/oaxaca/BBS_EndOfRun.txt
```

***If the directories and files do not apear updated when running `ls -l *` in the `nodes` directory, investigate the build server that appears to have a fault.<sup>4</sup>***

<hr/>
<sub>
1) This manual process of inspecting the build system should be automated.  A GH issue to track this problem has not yet been created.
<br/>2) For the purpose of automation, we should enumerate exactly which conditions must be met (e.g. exact files / directories updted by a specific time of day).
<br/>3) The perceval build server has been known to be slow.  We should create a ticket to investigate and resolve this issue.
<br/>4) TODO: Document and link to investigation steps for each build box.
</sub>
