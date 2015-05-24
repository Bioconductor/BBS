/*
Some packages (i.e. BrowserViz) start web browsers 
and require those web browsers to actually
be "smart" (i.e., have javascript, communicate over websockets).
Sometimes there are issues with starting "real" web browsers
in the build system context, even though everything *should* work
over Xvfb (it doesn't always). Luckily phantom.js is a "headless" browser
and works well.

So what we do in the case of BrowserViz is set an environment variable
called BROWSERVIZ_BROWSER and make it invoke phantomjs with this file, 
something like:

export BROWSERVIZ_BROWSER="phantomjs /path/to/headless_browser.js "

Then, BrowserViz has code like this:

.getBrowser <- function()
{
    if(nchar(Sys.getenv("BROWSERVIZ_BROWSER")))
        Sys.getenv("BROWSERVIZ_BROWSER")
    else
        getOption("browser")
}


And when we call browseURL, we do it like this:

  browseURL(uri, browser=.getBrowser())

R will append the URL to the command defined in the environment variable,
and the script below will look at its first argument to find the
URL to open.

When this environment variable is set properly, BrowserViz passes build
and check without issues.


 */



var page = require('webpage').create(),
    system = require('system');
var url = system.args[1];

page.open(url);

