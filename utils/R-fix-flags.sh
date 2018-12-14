#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

new_flag="-Wall"
cflags_line="^CFLAGS *=.*"
cxxflags_line="^CXXFLAGS *=.*"
cxx98flags_line="^CXX98FLAGS *=.*"
cxx11flags_line="^CXX11FLAGS *=.*"
cxx14flags_line="^CXX14FLAGS *=.*"
fflags_line="^FFLAGS *=.*"

mv -i Makeconf Makeconf.original

cat Makeconf.original \
	| sed -r "s/^($cflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cflags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxxflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxxflags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx98flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx98flags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx11flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx11flags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx14flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx14flags_line/\\0 $new_flag/" \
	| sed -r "s/^($fflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$fflags_line/\\0 $new_flag/" > Makeconf

set +e # because diff (below) will exit with status code 1

# Show the diff
echo "diff Makeconf Makeconf.original"
diff Makeconf Makeconf.original

exit 0
