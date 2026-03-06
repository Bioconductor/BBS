# .BBSoptions


The `.BBSoptions` file allows deviations from the default build behavior on a
per-package basis. The file is optional and if included should be located at
the root of the package directory. It should be in DCF format.


## Fields that control where to build/check the package

### UnsupportedPlatforms

Comma separated list of platforms not supported. Default is an empty
string.  Possible values are `win`, `win32`, `win64`, `mac`,
`mac.binary.big-sur-arm64`, `aarch64-linux-gnu`, or the name of a
build node. For example:

    UnsupportedPlatforms: win32, mac

or:

    UnsupportedPlatforms: tokay2, mac

### RunLongTests

`TRUE` or `FALSE` flag to trigger running of long tests. The default
is `FALSE`. To enable long tests set the field to `TRUE`:

    RunLongTests: TRUE

### GPU\_reliance

Value can be `optional` if the package can take advantage of a GPU when
present, or `required` if the presence of a GPU is actually _required_.
By _required_ we mean that the package won't be able to install or pass
build/check on a machine that does not have a GPU.

By default, i.e. if there's no `GPU_reliance` field, the package is
assumed to not try to use a GPU at all.


## Fields that alter the command used to build/check the package

### prepend fields

These fields inject an arbitrary string in front of the `R CMD INSTALL`,
`R CMD build` or `R CMD check` command. Default is an empty string.

Supported prepend fields:

- `INSTALLprepend`/`INSTALLprepend.win` for STAGE2.
- `BUILDprepend`/`BUILDprepend.win` for STAGE3.
- `CHECKprepend`/`CHECKprepend.win` for STAGE4.
- `BUILDBINprepend`/`BUILDBINprepend.win` for STAGE5.

By adding

    CHECKprepend: _R_CHECK_FORCE_SUGGESTS_=0

to the `.BBSoptions` file of package **foo**, the command used to check
**foo** during STAGE4 will be:

    _R_CHECK_FORCE_SUGGESTS_=0 path/to/R CMD check ...

This can be used to allow a package to try to pass `R CMD check` even
if some of the packages it `Suggests` couldn't be installed. The old way
of handling this was to use `Enhances` instead of `Suggests`.

To inject an arbitrary string in front of the `R CMD build` command used
during STAGE3 one could add:

    BUILDprepend: R_MAX_NUM_DLLS=150

to the `.BBSoptions` file. The command that will be used by the build
system to build **foo** during STAGE3 will then be:

    R_MAX_NUM_DLLS=150 path/to/R CMD build foo

### NoExamplesOnPlatforms

This field was created for a single special case. This field is NOT
recommended - use `UnsupportedPlatforms` instead.

Like for `UnsupportedPlatforms`, the value is expected to be a comma-separated
list of platforms where examples should not be run. Default is an empty string.
Possible values are `win`, `win32`, `win64`, `mac`, etc...

    NoExamplesOnPlatforms: win, mac


## Other fields

### Alert / AlertOn / AlertTo

These are not yet implemented but could be if there was a need. Notify package
maintainer of build failures or warnings.

- `Alert` enables `AlertOn` and `AlertTo`. Possible values are `TRUE`
   and `FALSE`. The default is `FALSE`. To enable alerts,

        Alert: TRUE

- `AlertOn` specifies which type of failure should trigger an alert. The
  default is ERROR.

  - To receive an alert in case of any warning on any platform:

        AlertOn: WARNINGS

  - To receive an alert in case of any error on any platform or any warning
    on Windows:

        AlertOn: ERROR, win.WARNINGS

  - To receive an alert in case of any error on malbec1 or any warning on
    Mac OS X

        AlertOn: malbec1.ERROR, mac.WARNINGS

- `AlertTo` specifies who should receive the alert message.

  The default value is the email address of the `Maintainer` found in
  the `DESCRIPTION` file of the package. More than one address can be
  specified, e.g.,

      AlertTo: userone@domain.org, user.two@domain.net

