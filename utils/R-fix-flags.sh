#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

new_flag="-Wall"
cflags_line="^CFLAGS *=.*"
cxxflags_line="^CXXFLAGS *=.*"
cxx11flags_line="^CXX11FLAGS *=.*"
cxx14flags_line="^CXX14FLAGS *=.*"
cxx17flags_line="^CXX17FLAGS *=.*"
cxx20flags_line="^CXX20FLAGS *=.*"
fcflags_line="^FCFLAGS *=.*"
fflags_line="^FFLAGS *=.*"

mv -i Makeconf Makeconf.original

cat Makeconf.original \
	| sed -r "s/^($cflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cflags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxxflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxxflags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx11flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx11flags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx14flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx14flags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx17flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx17flags_line/\\0 $new_flag/" \
	| sed -r "s/^($cxx20flags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx20flags_line/\\0 $new_flag/" \
	| sed -r "s/^($fcflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$fcflags_line/\\0 $new_flag/" \
	| sed -r "s/^($fflags_line) $new_flag +(.*)$/\\1 \\2/" \
	| sed -r "s/^$fflags_line/\\0 $new_flag/" > Makeconf

set +e # because diff (below) will exit with status code 1

# Show the diff
echo "diff Makeconf.original Makeconf"
diff Makeconf.original Makeconf

exit 0
