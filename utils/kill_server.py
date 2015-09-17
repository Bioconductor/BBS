#!/usr/bin/env python

import psutil

for p in psutil.process_iter():
	try:
		cmdline = p.cmdline()
		if len(cmdline) == 2 and cmdline[0] == 'python' and \
		  cmdline[1] == 'server.py':
		      p.kill()
		      break
	except:
		pass