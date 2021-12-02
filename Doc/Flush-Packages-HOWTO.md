# Flushing the Software Repository

To remove stale software packages, we flush the software repository. This might
be necessary when a build machine has transition from devel to release to
try to remove odd version-numbered packages.

It's important to reserve enough time and carefully check the results of the
report so that it doesn't negatively impact users.

The following are instructions to flush the software repository for the 3.14
builds as an example.

## Check the Day's Report

Verify that the software report for the day looks good and that you have at
least an hour before the next build. Look for packages, such as
`GenomicFeatures`, that are dependencies for many packages and ensure that they
are not failing. If they are failing, you should wait until they are passing
before attempting to flush the software repository.

# Comment Out Software Propagation in the Crontab

As `biocpush`, comment out the crontab entry for bioc. This will prevent
master from resyncing with staging on the build machine you're working on.

## Make a Backup

Create a backup of the software packages in case a package that is a dependency
for several packages, such as `GenomicFeatures`, that was passing later fails
in the new build report after removing all packages.

As `biocpush`

    cd ~biocpush/PACKAGES/3.14/
    cp -r bioc bioc.backup

## Remove All Packages

Remove all packages from `~biocpush/PACKAGES/3.14/bioc` for source, windows,
and mac binaries. Everything except for the `Archives` directories should be
gone and the `PACKAGES` files should be replaced with blank files.

As `biocpush`

    cd ~biocpush/PACKAGES/3.14/src/contrib
    rm -r PACKAGES* *.gz
    touch PACKAGES
    cd ~biocpush/PACKAGES/3.14/macosx/contrib/4.1
    rm -r PACKAGES* *.tgz
    touch PACKAGES
    cd ~biocpush/PACKAGES/3.14/windows/contrib/4.1
    rm -r PACKAGES* *.zip
    touch PACKAGES

## Rerun the `postrun.sh`

As `biocbuild` rerun `postrun.sh` so that we get a new report. Check that the
new report has green leds and that important packages, such as
`GenomicFeatures`, pass so that we don't have a lot of failures.

If the report is not good, replace `bioc` with `bioc.backup` and rerun the
`postrun.sh`.

## Manually Run `updateReposPkgs-bioc.sh`

If the report is good, manually run `updateReposPkgs-bioc.sh` as `biocpush`.

## Uncomment Software Propagation in the Crontab

When everything is finished, uncomment the bioc propagation line in the
crontab.
