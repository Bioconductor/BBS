#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 19, 2010
###
### html module
###

import codecs
import unicodedata
import cgi

### Dictionary of HTML entities not covered by cgi.escape().
### Add more entries as needed (see tables of entities at
### http://www.zytrax.com/tech/web/entities.html).
unicodename2htmlentity = { \
    'QUOTATION MARK': '&quot;', # u'\x22'
    'AMPERSAND': '&amp;', # u'\x26'
    'LESS-THAN SIGN': '&lt;', # u'\x3c'
    'GREATER-THAN SIGN': '&gt;', # u'\x3e'
    'TILDE': '&tilde;', # u'\x7e'
    'NO-BREAK SPACE': '&nbsp;', # u'\xa0'
    'INVERTED EXCLAMATION MARK': '&iexcl;', # u'\xa1'
    'CENT SIGN': '&cent;', # u'\xa2'
    'POUND SIGN': '&pound;', # u'\xa3'
    'CURRENCY SIGN': '&curren;', # u'\xa4'
    'YEN SIGN': '&yen;', # u'\xa5'
    'BROKEN BAR': '&brvbar;', # u'\xa6'
    'SECTION SIGN': '&sect;', # u'\xa7'
    'DIAERESIS': '&uml;', # u'\xa8'
    'COPYRIGHT SIGN': '&copy;', # u'\xa9'
    'FEMININE ORDINAL INDICATOR': '&ordf;', # u'\xaa'
    'LEFT-POINTING DOUBLE ANGLE QUOTATION MARK': '&laquo;', # u'\xab'
    'NOT SIGN': '&not;', # u'\xac'
    'SOFT HYPHEN': '&shy;', # u'\xad'
    'REGISTERED SIGN': '&reg;', # u'\xae'
    'MACRON': '&macr;', # u'\xaf'
    'DEGREE SIGN': '&deg;', # u'\xb0'
    'PLUS-MINUS SIGN': '&plusmn;', # u'\xb1'
    'SUPERSCRIPT TWO': '&sup2;', # u'\xb2'
    'SUPERSCRIPT THREE': '&sup3;', # u'\xb3'
    'ACUTE ACCENT': '&acute;', # u'\xb4'
    'MICRO SIGN': '&micro;', # u'\xb5'
    'PILCROW SIGN': '&para;', # u'\xb6'
    'MIDDLE DOT': '&middot;', # u'\xb7'
    'CEDILLA': '&cedil;', # u'\xb8'
    'SUPERSCRIPT ONE': '&sup1;', # u'\xb9'
    'MASCULINE ORDINAL INDICATOR': '&ordm;', # u'\xba'
    'RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK': '&raquo;', # u'\xbb'
    'VULGAR FRACTION ONE QUARTER': '&frac14;', # u'\xbc'
    'VULGAR FRACTION ONE HALF': '&frac12;', # u'\xbd'
    'VULGAR FRACTION THREE QUARTERS': '&frac34;', # u'\xbe'
    'INVERTED QUESTION MARK': '&iquest;', # u'\xbf'
    'LATIN CAPITAL LETTER A WITH GRAVE': '&Agrave;', # u'\xc0'
    'LATIN CAPITAL LETTER A WITH ACUTE': '&Aacute;', # u'\xc1'
    'LATIN CAPITAL LETTER A WITH CIRCUMFLEX': '&Acirc;', # u'\xc2'
    'LATIN CAPITAL LETTER A WITH TILDE': '&Atilde;', # u'\xc3'
    'LATIN CAPITAL LETTER A WITH DIAERESIS': '&Auml;', # u'\xc4'
    'LATIN CAPITAL LETTER A WITH RING ABOVE': '&Aring;', # u'\xc5'
    'LATIN CAPITAL LETTER AE': '&AElig;', # u'\xc6'
    'LATIN CAPITAL LETTER C WITH CEDILLA': '&Ccedil;', # u'\xc7'
    'LATIN CAPITAL LETTER E WITH GRAVE': '&Egrave;', # u'\xc8'
    'LATIN CAPITAL LETTER E WITH ACUTE': '&Eacute;', # u'\xc9'
    'LATIN CAPITAL LETTER E WITH CIRCUMFLEX': '&Ecirc;', # u'\xca'
    'LATIN CAPITAL LETTER E WITH DIAERESIS': '&Euml;', # u'\xcb'
    'LATIN CAPITAL LETTER I WITH GRAVE': '&Igrave;', # u'\xcc'
    'LATIN CAPITAL LETTER I WITH ACUTE': '&Iacute;', # u'\xcd'
    'LATIN CAPITAL LETTER I WITH CIRCUMFLEX': '&Icirc;', # u'\xce'
    'LATIN CAPITAL LETTER I WITH DIAERESIS': '&Iuml;', # u'\xcf'
    'LATIN CAPITAL LETTER ETH': '&ETH;', # u'\xd0'
    'LATIN CAPITAL LETTER N WITH TILDE': '&Ntilde;', # u'\xd1'
    'LATIN CAPITAL LETTER O WITH GRAVE': '&Ograve;', # u'\xd2'
    'LATIN CAPITAL LETTER O WITH ACUTE': '&Oacute;', # u'\xd3'
    'LATIN CAPITAL LETTER O WITH CIRCUMFLEX': '&Ocirc;', # u'\xd4'
    'LATIN CAPITAL LETTER O WITH TILDE': '&Otilde;', # u'\xd5'
    'LATIN CAPITAL LETTER O WITH DIAERESIS': '&Ouml;', # u'\xd6'
    'MULTIPLICATION SIGN': '&times;', # u'\xd7'
    'LATIN CAPITAL LETTER O WITH STROKE': '&Oslash;', # u'\xd8'
    'LATIN CAPITAL LETTER U WITH GRAVE': '&Ugrave;', # u'\xd9'
    'LATIN CAPITAL LETTER U WITH ACUTE': '&Uacute;', # u'\xda'
    'LATIN CAPITAL LETTER U WITH CIRCUMFLEX': '&Ucirc;', # u'\xdb'
    'LATIN CAPITAL LETTER U WITH DIAERESIS': '&Uuml;', # u'\xdc'
    'LATIN CAPITAL LETTER Y WITH ACUTE': '&Yacute;', # u'\xdd'
    'LATIN CAPITAL LETTER THORN': '&THORN;', # u'\xde'
    'LATIN SMALL LETTER SHARP S': '&szlig;', # u'\xdf'
    'LATIN SMALL LETTER A WITH GRAVE': '&agrave;', # u'\xe0'
    'LATIN SMALL LETTER A WITH ACUTE': '&aacute;', # u'\xe1'
    'LATIN SMALL LETTER A WITH CIRCUMFLEX': '&acirc;', # u'\xe2'
    'LATIN SMALL LETTER A WITH TILDE': '&atilde;', # u'\xe3'
    'LATIN SMALL LETTER A WITH DIAERESIS': '&auml;', # u'\xe4'
    'LATIN SMALL LETTER A WITH RING ABOVE': '&aring;', # u'\xe5'
    'LATIN SMALL LETTER AE': '&aelig;', # u'\xe6'
    'LATIN SMALL LETTER C WITH CEDILLA': '&ccedil;', # u'\xe7'
    'LATIN SMALL LETTER E WITH GRAVE': '&egrave;', # u'\xe8'
    'LATIN SMALL LETTER E WITH ACUTE': '&eacute;', # u'\xe9'
    'LATIN SMALL LETTER E WITH CIRCUMFLEX': '&ecirc;', # u'\xea'
    'LATIN SMALL LETTER E WITH DIAERESIS': '&euml;', # u'\xeb'
    'LATIN SMALL LETTER I WITH GRAVE': '&igrave;', # u'\xec'
    'LATIN SMALL LETTER I WITH ACUTE': '&iacute;', # u'\xed'
    'LATIN SMALL LETTER I WITH CIRCUMFLEX': '&icirc;', # u'\xee'
    'LATIN SMALL LETTER I WITH DIAERESIS': '&iuml;', # u'\xef'
    'LATIN SMALL LETTER ETH': '&eth;', # u'\xf0'
    'LATIN SMALL LETTER N WITH TILDE': '&ntilde;', # u'\xf1'
    'LATIN SMALL LETTER O WITH GRAVE': '&ograve;', # u'\xf2'
    'LATIN SMALL LETTER O WITH ACUTE': '&oacute;', # u'\xf3'
    'LATIN SMALL LETTER O WITH CIRCUMFLEX': '&ocirc;', # u'\xf4'
    'LATIN SMALL LETTER O WITH TILDE': '&otilde;', # u'\xf5'
    'LATIN SMALL LETTER O WITH DIAERESIS': '&ouml;', # u'\xf6'
    'DIVISION SIGN': '&divide;', # u'\xf7'
    'LATIN SMALL LETTER O WITH STROKE': '&oslash;', # u'\xf8'
    'LATIN SMALL LETTER U WITH GRAVE': '&ugrave;', # u'\xf9'
    'LATIN SMALL LETTER U WITH ACUTE': '&uacute;', # u'\xfa'
    'LATIN SMALL LETTER U WITH CIRCUMFLEX': '&ucirc;', # u'\xfb'
    'LATIN SMALL LETTER U WITH DIAERESIS': '&uuml;', # u'\xfc'
    'LATIN SMALL LETTER Y WITH ACUTE': '&yacute;', # u'\xfd'
    'LATIN SMALL LETTER THORN': '&thorn;', # u'\xfe'
    'LATIN SMALL LETTER Y WITH DIAERESIS': '&yuml;', # u'\xff'
    'LEFT SINGLE QUOTATION MARK': '&lsquo;', # u'\u2018'
    'RIGHT SINGLE QUOTATION MARK': '&rsquo;', # u'\u2019'
    'LEFT DOUBLE QUOTATION MARK': '&ldquo;', # u'\u201c'
    'RIGHT DOUBLE QUOTATION MARK': '&rdquo;' # u'\u201d'
}

def encodeHTMLentities(text, encoding):
    ## See http://docs.python.org/library/codecs.html for the list of
    ## encodings and for more info about codecs in Python.
    decoder = codecs.getdecoder(encoding)
    try:
        utext = decoder(text)[0]  # converts text to Unicode
    except:
        return text
    html = ''
    for char in utext:
        try:
            unicodename = unicodedata.name(char)
            html += unicodename2htmlentity[unicodename]
        except:
            html += cgi.escape(char)
    return html

if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

