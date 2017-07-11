#!/bin/bash
#
#set -e # Exit immediately if a simple command exits with a non-zero status.

print_help()
{
	cat <<-EOD
	Usage:

	 1) To bump package version string:

	      $0 [even|odd] [test]

	    Bumps the version strings (expected format is "x.y.z")
	    of all packages found in the current directory
	    to next y (or to next even y if option 'even' is specified,
	    or to next odd y if option 'odd' is specified).
	    Doesn't perform any change (just simulate) with option 'test'.

	 2) To do some "pre-bumping" stats:

	      $0 {list|bad}

	    list:    Displays the list of all packages found in the
	             current directory.
	    bad:     Displays the version strings with bad format.

	 3) To do some "post-bumping" stats/operation:

	      $0 {diff|restore|clean}

	    diff:    Diffs between original and updated DESCRIPTION files.
	    restore: Restores the original DESCRIPTION files.
	    clean:   Removes the original DESCRIPTION files.

	 4) Other stats:

	      $0 field <fieldname>

	    Displays 2 lists of packages: those having a field named
	    <fieldname> in their DESCRIPTION file, and those that don't.
	EOD
	exit 1
}

if [ "$1" != "" ]; then
	help_needed="yes"
	opt_list="even odd test list bad diff restore clean field"
	for opt in $opt_list; do
		if [ "$1" == "$opt" ]; then
			help_needed="no"
			break
		fi
	done
	if [ "$help_needed" == "yes" ]; then
		print_help
	fi
fi

if [ "$1" == "test" ] || [ "$2" == "test" ]; then
	test="yes"
fi

BACKUP_EXT=".original"
# WARNING: The last whitespace in the regexp below MUST be a tab. Don't remove!
#EOK_REGEXP=":( |	)"
# Because SuppDists/DESCRIPTION has no whitespace between "Package:" and "SuppDists"
EOK_REGEXP=":" 
VERSION_LINE_REGEXP="^Version$EOK_REGEXP[[:space:]]*([^[:space:]].*[^[:space:]])[[:space:]]*$"
NB_REGEXP="(0|[1-9][0-9]*)"
VERSION_REGEXP="^($NB_REGEXP)(\.|-)($NB_REGEXP)(\.|-)($NB_REGEXP)$"


# ----------------------------------------------------------------------------
ls_out=`ls`

# In order to work with the packages that are listed in the manifest file
# only, cd to the Rpacks dir, then do:
#   grep 'Package: ' bioc_1.8.manifest | sed 's/Package: //g' > bump.list
# then uncomment the line below:
#ls_out=`cat bump.list`

pkg_list=""
nodesc_list=""
for pkg in $ls_out; do
	if [ ! -d "$pkg" ]; then
		continue
	fi
	desc_file="$pkg/DESCRIPTION"
	if [ ! -f "$desc_file" ]; then
		nodesc_list="$nodesc_list$pkg "
		continue
	fi
	line=`grep -E "^Version$EOK_REGEXP" $desc_file`
	if [ $? -ne 0 ]; then
		echo "ERROR: File $desc_file has no 'Version' field!"
		exit 2
	fi
	pkg_list="$pkg_list$pkg "
done


# ----------------------------------------------------------------------------
if [ "$1" == "list" ]; then
	echo ""
	nb_pkgs=`echo $pkg_list | wc -w`
	echo "$nb_pkgs dir(s) found with a DESCRIPTION file:"
	echo "$pkg_list"
	echo ""
	nb_nodesc_dirs=`echo $nodesc_list | wc -w`
	echo "$nb_nodesc_dirs dir(s) found without DESCRIPTION file:"
	echo "$nodesc_list"
	exit 0
fi


# ----------------------------------------------------------------------------
if [ "$1" == "field" ]; then
	if [ "$2" == "" ]; then
		print_help
	fi
	field="$2"
	echo "Searching packages having field '$field' in their DESCRIPTION file..."
	having_pkgs=""
	not_having_pkgs=""
	for pkg in $pkg_list; do
		desc_file="$pkg/DESCRIPTION"
		line=`grep -E "^$field$EOK_REGEXP" $desc_file`
		if [ $? -ne 0 ]; then
			not_having_pkgs="$not_having_pkgs$pkg "
			continue
		fi
		echo "In $desc_file: $line"
		having_pkgs="$having_pkgs$pkg "
	done
	echo ""
	nb_having=`echo $having_pkgs | wc -w`
	echo "$nb_having package(s) found having field '$field' in their DESCRIPTION file:"
	echo "$having_pkgs"
	echo ""
	nb_not_having=`echo $not_having_pkgs | wc -w`
	echo "$nb_not_having package(s) found NOT having field '$field' in their DESCRIPTION file:"
	echo "$not_having_pkgs"
	exit 0
fi


# ----------------------------------------------------------------------------
if [ "$1" == "diff" ]; then
	for pkg in $pkg_list; do
		desc_file="$pkg/DESCRIPTION"
		backup_desc_file="$desc_file$BACKUP_EXT"
		echo "diff $backup_desc_file $desc_file"
		diff "$backup_desc_file" "$desc_file"
		continue
	done
	exit 0
fi


# ----------------------------------------------------------------------------
if [ "$1" == "restore" ]; then
	restored_pkg_list=""
	for pkg in $pkg_list; do
		desc_file="$pkg/DESCRIPTION"
		backup_desc_file="$desc_file$BACKUP_EXT"
		if [ ! -f "$backup_desc_file" ]; then
			continue
		fi
		restored_pkg_list="$restored_pkg_list$pkg "
		mv -f "$backup_desc_file" "$desc_file"
	done
	echo ""
	nb_restored=`echo $restored_pkg_list | wc -w`
	echo "$nb_restored package(s) have had their DESCRIPTION file restored:"
	echo "$restored_pkg_list"
	exit 0
fi


# ----------------------------------------------------------------------------
if [ "$1" == "clean" ]; then
	cleaned_pkg_list=""
	for pkg in $pkg_list; do
		desc_file="$pkg/DESCRIPTION"
		backup_desc_file="$desc_file$BACKUP_EXT"
		if [ ! -f "$backup_desc_file" ]; then
			continue
		fi
		cleaned_pkg_list="$cleaned_pkg_list$pkg "
		rm -f "$backup_desc_file" 
	done
	echo ""
	nb_cleaned=`echo $cleaned_pkg_list | wc -w`
	echo "$nb_cleaned package(s) have been cleaned:"
	echo "$cleaned_pkg_list"
	exit 0
fi


# ----------------------------------------------------------------------------
if [ "$test" == "yes" ]; then
	verb="will be updated to"
else
	verb="is being updated to"
fi
updated_pkg_list=""
notupdated_pkg_list=""
for pkg in $pkg_list; do
	desc_file="$pkg/DESCRIPTION"
	backup_desc_file="$desc_file$BACKUP_EXT"
	old_line=`grep -E "^Version$EOK_REGEXP" $desc_file`
	version_string=`echo $old_line | sed -r "s/$VERSION_LINE_REGEXP/\1/"`
	echo "$version_string" | grep -E "$VERSION_REGEXP" > /dev/null
	if [ $? -ne 0 ]; then
		echo "Package $pkg"
		echo "  Current version is $version_string: Bad format!"
		notupdated_pkg_list="$notupdated_pkg_list$pkg "
		continue
	fi
	if [ "$1" == "bad" ]; then
		continue;
	fi
	x=`echo $version_string | sed -r "s/$VERSION_REGEXP/\1/"`
	y=`echo $version_string | sed -r "s/$VERSION_REGEXP/\4/"`
	z=`echo $version_string | sed -r "s/$VERSION_REGEXP/\7/"`
	echo "Package $pkg"
	echo -n "  Current version is $version_string (x=$x y=$y z=$z) "
	updated_pkg_list="$updated_pkg_list$pkg "
	(( parity=$y%2 ))
	if [ "$1" == "even" ]; then
		if [ $parity -eq 1 ]; then
			echo -n "(ODD y) "
			(( y=$y+1 ))
			action="y->y+1"
		else
			echo -n "(EVEN y) "
			(( y=$y+2 ))
			action="y->y+2"
		fi
	elif [ "$1" == "odd" ]; then
		if [ $parity -eq 1 ]; then
			echo -n "(ODD y) "
			(( y=$y+2 ))
			action="y->y+2"
		else
			echo -n "(EVEN y) "
			(( y=$y+1 ))
			action="y->y+1"
		fi
	else
		(( y=$y+1 ))
		action="y->y+1"
	fi
	if [ $y -eq 100 ]; then
		(( x=$x+1 ))
		y=0
		action="x->x+1,y->0"
	fi
	new_version_string="$x.$y.0"
	echo "==> $verb $new_version_string ($action)"
	if [ "$test" == "yes" ]; then
		continue
	fi
	new_line="Version: $new_version_string"
	mv -i "$desc_file" "$backup_desc_file"
	sed "s/$old_line/$new_line/" "$backup_desc_file" > "$desc_file"
done

if [ "$1" == "bad" ]; then
	exit 0
fi


# ----------------------------------------------------------------------------
echo ""
if [ "$test" == "yes" ]; then
	verb="will have"
else
	verb="had"
fi
nb_updated=`echo $updated_pkg_list | wc -w`
echo "$nb_updated package(s) $verb their DESCRIPTION file updated:"
echo "$updated_pkg_list"

echo ""
if [ "$test" == "yes" ]; then
	verb="will NOT have"
else
	verb="had NOT"
fi
nb_notupdated=`echo $notupdated_pkg_list | wc -w`
echo -n "$nb_notupdated package(s) $verb their DESCRIPTION file"
echo " updated because they have a version string with bad format:"
echo "$notupdated_pkg_list"

echo ""
echo "Rerun with option 'bad' to see the version strings with bad format..."

if [ "$test" == "yes" ]; then
	exit 0
fi


# ----------------------------------------------------------------------------
echo ""
echo "DONE."
echo ""
echo "The original DESCRIPTION files have been saved under DESCRIPTION$BACKUP_EXT."
echo "Rerun with option 'restore' to restore them..."
echo "Or, if everything looks OK, remove them by using option 'clean'..."
