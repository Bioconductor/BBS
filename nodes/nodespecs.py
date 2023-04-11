### allnodes['nebbiolo1'] is a dict with 5 keys: 'OS', 'Arch', 'Platform',
### 'pkgType', and 'encoding'. The value in each key-value pair must be
### a string.
### 'pkgType' is the native package type for the node (must be one of "source",
### "win.binary", "win64.binary", "mac.binary", "mac.binary.leopard",
### or "mac.binary.mavericks").
### 'encoding' must be an encoding accepted by Python function
### codecs.getdecoder() (test it from python with e.g.
### codecs.getdecoder('utf_8') or codecs.getdecoder('iso8859'))

# FIXME - parameterize this as much as possible
# OS version, etc.. can be obtained programmatically

allnodes = {
    'nebbiolo1':  {'OS'      : "Linux (Ubuntu 22.04.1 LTS)",
                   'Arch'    : "x86_64",
                   'Platform': "x86_64-linux-gnu",
                   'pkgType' : "source",
                   'encoding': "utf_8"},
    'nebbiolo2':  {'OS'      : "Linux (Ubuntu 20.04.5 LTS)",
                   'Arch'    : "x86_64",
                   'Platform': "x86_64-linux-gnu",
                   'pkgType' : "source",
                   'encoding': "utf_8"},
    'riesling1':  {'OS'      : "Windows Server 2019 Standard",
                   'Arch'    : "x64",
                   'Platform': "mingw32 / x86_64-w64-mingw32",
                   'pkgType' : "win.binary",
                   'encoding': "iso8859"},
    'palomino3':  {'OS'      : "Windows Server 2022 Datacenter",
                   'Arch'    : "x64",
                   'Platform': "x86_64-w64-mingw32",
                   'pkgType' : "win.binary",
                   'encoding': "iso8859"},
    'palomino4':  {'OS'      : "Windows Server 2022 Datacenter",
                   'Arch'    : "x64",
                   'Platform': "x86_64-w64-mingw32",
                   'pkgType' : "win.binary",
                   'encoding': "iso8859"},
    'kjohnson':   {'OS'      : "macOS 13.0 Ventura",
                   'Arch'    : "arm64",
                   'Platform': "arm64-apple-darwin22.1.0",
                   'pkgType' : "mac.binary.big-sur-arm64",
                   'encoding': "utf-8"},
    'kjohnson2':  {'OS'      : "macOS 12.6.1 Monterey",
                   'Arch'    : "arm64",
                   'Platform': "arm64-apple-darwin21.6.0",
                   'pkgType' : "mac.binary.big-sur-arm64",
                   'encoding': "utf-8"},
    'lconway':    {'OS'      : "macOS 12.5.1 Monterey",
                   'Arch'    : "x86_64",
                   'Platform': "x86_64-apple-darwin21.6.0",
                   'pkgType' : "mac.binary",
                   'encoding': "utf-8"},
    'merida1':    {'OS'      : "macOS 12.6.4 Monterey",
                   'Arch'    : "x86_64",
                   'Platform': "x86_64-apple-darwin21.6.0",
                   'pkgType' : "mac.binary",
                   'encoding': "utf-8"}
}
