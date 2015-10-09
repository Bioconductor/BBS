# This script should be run periodically (once an hour?)
# via task manager (as biocbuild user)
# on windows 2012 build machines. 

# Why? Because if a package calls vignette() on a pdf
# vignette, that will start miktex-texworks.exe
# (miktex's pdf viewer) and the miktex-texworks
# process will hold on to one of the build directories
# so that when the next build starts it will not be able
# to (re-)create the build directories, which will
# cause the entire build to fail!

# This only seems to happen on windows 2012. I wonder
# if the same thing would happen if we had a different 
# default pdf viewer set up. But then file associations
# seem not to work well via scheduled tasks, see 
# https://stat.ethz.ch/pipermail/r-help/2015-August/431411.html

import psutil
import os

for p in psutil.process_iter():
    try:
      if p.name() == 'miktex-texworks.exe':
        os.kill(p.pid, 9)
    except:
      pass

