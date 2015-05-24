#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

# does the value of mtune vary with the number of cores?
old_lineA="CFLAGS = -mtune=core2 -g -O2"
new_lineA="CFLAGS = -mtune=core2 -g -O2 -Wall"
old_lineB="CXXFLAGS = -mtune=core2 -g -O2"
new_lineB="CXXFLAGS = -mtune=core2 -g -O2 -Wall"
old_lineC="FFLAGS = -g -O2"
new_lineC="FFLAGS = -g -O2 -Wall"

mv -i Makeconf Makeconf.original
cp Makeconf.original Makeconf.3
cat Makeconf.3 | sed "s/^$old_lineA/$new_lineA/" > Makeconf.2
cat Makeconf.2 | sed "s/^$old_lineB/$new_lineB/" > Makeconf.1
cat Makeconf.1 | sed "s/^$old_lineC/$new_lineC/" > Makeconf.0
cp Makeconf.0 Makeconf
rm Makeconf.?
