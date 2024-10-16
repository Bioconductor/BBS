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
    ## Non-building central nodes on Jetstream2.
    'bbscentral1': {'OS'      : "Linux (Ubuntu 22.04.4 LTS)",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf_8"},
    'bbscentral2': {'OS'      : "Linux (Ubuntu 22.04.4 LTS)",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf_8"},
    ## Internal build nodes.
    'nebbiolo1':   {'OS'      : "Linux (Ubuntu 22.04.3 LTS)",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf_8"},
    'nebbiolo2':   {'OS'      : "Linux (Ubuntu 24.04.1 LTS)",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf_8"},
    'teran2':      {'OS'      : "Linux (Ubuntu 24.04.1 LTS)",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf_8"},
    'palomino7':   {'OS'      : "Windows Server 2022 Datacenter",
                    'Arch'    : "x64",
                    'Platform': "x86_64-w64-mingw32",
                    'pkgType' : "win.binary",
                    'encoding': "iso8859"},
    'palomino8':   {'OS'      : "Windows Server 2022 Datacenter",
                    'Arch'    : "x64",
                    'Platform': "x86_64-w64-mingw32",
                    'pkgType' : "win.binary",
                    'encoding': "iso8859"},
    'kjohnson1':   {'OS'      : "macOS 13.6.6 Ventura",
                    'Arch'    : "arm64",
                    'Platform': "arm64-apple-darwin22.6.0",
                    'pkgType' : "mac.binary.big-sur-arm64",
                    'encoding': "utf-8"},
    'kjohnson3':   {'OS'      : "macOS 13.6.5 Ventura",
                    'Arch'    : "arm64",
                    'Platform': "arm64-apple-darwin22.6.0",
                    'pkgType' : "mac.binary.big-sur-arm64",
                    'encoding': "utf-8"},
    'lconway':     {'OS'      : "macOS 12.7.1 Monterey",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-apple-darwin21.6.0",
                    'pkgType' : "mac.binary.big-sur-x86_64",
                    'encoding': "utf-8"},
    'merida1':     {'OS'      : "macOS 12.7.5 Monterey",
                    'Arch'    : "x86_64",
                    'Platform': "x86_64-apple-darwin21.6.0",
                    'pkgType' : "mac.binary.big-sur-x86_64",
                    'encoding': "utf-8"},
    ## External nodes.
    'kunpeng2':    {'OS'      : "Linux (openEuler 22.03 LTS-SP1)",
                    'Arch'    : "aarch64",
                    'Platform': "aarch64-linux-gnu",
                    'pkgType' : "source",
                    'encoding': "utf-8",
                    'displayOnHTMLReport': "See Martin Grigorov's <a target=\"_blank\" href=\"https://bioconductor.github.io/biocblog/posts/2023-06-09-debug-linux-arm64-on-docker/\">blog post</a> for how to debug Linux ARM64 related issues on a x86_64 host."}
}
