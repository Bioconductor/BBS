#!/bin/bash

set -e  # exit immediately if a simple command exits with a non-zero status

new_flags="-Wall -Werror=format-security"
new_fflags="-Wall"  # -Werror=format-security not valid for Fortran

if [[ $# -eq 1 && $1 == "-y" ]]; then
	echo "Applying $new_flags"
else
	echo "Add '$new_flags' to *FLAGS?"
	echo ""
	echo "IMPORTANT NOTE: Only do this for BioC >= 3.21 + R >= 4.5."
	echo "If you're installing R < 4.5 (for BioC < 3.21 builds), then"
	echo "use the R-fix-flags-old.sh script instead."
	echo ""
	while true; do
		read -p "Please answer yes or no: " yn
		case $yn in
			[Yy]* ) break;;
			[Nn]* ) exit;;
			* ) ;;
		esac
	done
fi

cflags_line="^CFLAGS *=.*"
cxxflags_line="^CXXFLAGS *=.*"
cxx11flags_line="^CXX11FLAGS *=.*"
cxx14flags_line="^CXX14FLAGS *=.*"
cxx17flags_line="^CXX17FLAGS *=.*"
cxx20flags_line="^CXX20FLAGS *=.*"
cxx23flags_line="^CXX23FLAGS *=.*"
fcflags_line="^FCFLAGS *=.*"
fflags_line="^FFLAGS *=.*"

if [[ $# -eq 1 && $1 == "noninteractive" ]]; then
	mv Makeconf Makeconf.original
else
	mv -i Makeconf Makeconf.original
fi

cat Makeconf.original \
	| sed -r "s/^($cflags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cflags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxxflags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxxflags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxx11flags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx11flags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxx14flags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx14flags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxx17flags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx17flags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxx20flags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx20flags_line/\\0 $new_flags/" \
	| sed -r "s/^($cxx23flags_line) $new_flags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$cxx23flags_line/\\0 $new_flags/" \
	| sed -r "s/^($fcflags_line) $new_fflags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$fcflags_line/\\0 $new_fflags/" \
	| sed -r "s/^($fflags_line) $new_fflags +(.*)$/\\1 \\2/" \
	| sed -r "s/^$fflags_line/\\0 $new_fflags/" > Makeconf

set +e  # because diff (below) will exit with status code 1

# Show the diff
echo "diff Makeconf.original Makeconf"
diff Makeconf.original Makeconf

exit 0
