#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

old_flags="(-g -O2?( \\$\(LTO\))?) ?"
new_flags="\\1 -Wall"

old_lineA="CFLAGS = $old_flags"
new_lineA="CFLAGS = $new_flags"
old_lineB="CXXFLAGS = $old_flags"
new_lineB="CXXFLAGS = $new_flags"
old_lineC="FFLAGS = $old_flags"
new_lineC="FFLAGS = $new_flags"

mv -i Makeconf Makeconf.original
cp Makeconf.original Makeconf.3
cat Makeconf.3 | sed -r "s/^$old_lineA$/$new_lineA/" > Makeconf.2
cat Makeconf.2 | sed -r "s/^$old_lineB$/$new_lineB/" > Makeconf.1
cat Makeconf.1 | sed -r "s/^$old_lineC$/$new_lineC/" > Makeconf.0
cp Makeconf.0 Makeconf
rm Makeconf.?

# Show the diff
echo "diff Makeconf Makeconf.original"
diff Makeconf Makeconf.original

