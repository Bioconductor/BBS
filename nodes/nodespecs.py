### allnodes['lamb1'] is a tuple of 5 elements: OS, Arch, Platform, pkgType,
### encoding. Each element must be a string.
### 'pkgType' is the native package type for the node (must be one of "source",
### "win.binary", "win64.binary", "mac.binary", "mac.binary.leopard",
### or "mac.binary.mavericks").
### 'encoding' must be an encoding accepted by Python function
### codecs.getdecoder() (test it from python with e.g.
### codecs.getdecoder('utf_8') or codecs.getdecoder('iso8859'))

# FIXME - parameterize this as much as possible
# OS version, etc. can be obtained programmatically

allnodes = {
    'malbec1':    ("Linux (Ubuntu 16.04.1 LTS)",
                   "x86_64",
                   "x86_64-linux-gnu",
                   "source",
                   "utf_8"),
    'malbec2':    ("Linux (Ubuntu 18.04.1 LTS)",
                   "x86_64",
                   "x86_64-linux-gnu",
                   "source",
                   "utf_8"),
    'moscato1':   ("Windows Server 2008 R2 Standard (64-bit)",
                   "x64",
                   "mingw32 / x86_64-w64-mingw32",
                   "win.binary",
                   "iso8859"),
    'moscato2':   ("Windows Server 2008 R2 Enterprise SP1 (64-bit)",
                   "x64",
                   "mingw32 / x86_64-w64-mingw32",
                   "win.binary",
                   "iso8859"),
    'tokay1':     ("Windows Server 2012 R2 Standard",
                   "x64",
                   "mingw32 / x86_64-w64-mingw32",
                   "win.binary",
                   "iso8859"),
    'tokay2':     ("Windows Server 2012 R2 Standard",
                   "x64",
                   "mingw32 / x86_64-w64-mingw32",
                   "win.binary",
                   "iso8859"),
    'veracruz1':  ("OS X 10.11.6 El Capitan",
                   "x86_64",
                   "x86_64-apple-darwin15.6.0",
                   "mac.binary.el-capitan",
                   "utf-8"),
    'veracruz2':  ("OS X 10.11.6 El Capitan",
                   "x86_64",
                   "x86_64-apple-darwin15.6.0",
                   "mac.binary.el-capitan",
                   "utf-8"),
    'merida1':    ("OS X 10.11.6 El Capitan",
                   "x86_64",
                   "x86_64-apple-darwin15.6.0",
                   "mac.binary.el-capitan",
                   "utf-8"),
    'merida2':    ("OS X 10.11.6 El Capitan",
                   "x86_64",
                   "x86_64-apple-darwin15.6.0",
                   "mac.binary.el-capitan",
                   "utf-8")
    'celaya2':    ("OS X 10.11.6 El Capitan",
                   "x86_64",
                   "x86_64-apple-darwin15.6.0",
                   "mac.binary.el-capitan",
                   "utf-8")
}
