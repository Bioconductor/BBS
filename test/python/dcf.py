import re

class DcfRecordParser(object):
    """A class to parse Debian Control Format (DCF) files.

    DCF files look like this:

        key1: value1
        key2: value2
        key3: a value that
              continues must start the line with white space
        key4: another value

    There must not be blank lines between key/value lines.

    This class is initialized with a file-like object (not a path) and
    upon init it parses the DCF file raising a DCFParseError if it encounters
    badness.
  
    Call the getValue(field) to obtain the value for key "field".  Note that if
    there is no value defined for the key you will have to trap the error.

    """
    def __init__(self, file):
        """Create a new instance representing the DCF formatted data contained 
        in the file-like object (not path) file.
        """
        self.file = file
        self._dataDict = None
        self._parseRecord()

    def getValue(self, field):
        """Return the value associated with the specified field.

        If no such value, raise a KeyError.
        """
        return self._dataDict[field]

    def _parseRecord(self):
        """Parse a single DCF record (group of key/value lines)."""
        rec = {}
        key = None
        for line in self.file:
            if not self._isContinuation(line):
                pos = line.find(':')
                if pos > 0:
                    key = line[0:pos]
                    val = line[pos+1:]
                    rec[key] = val.strip()
                else:
                    raise DCFParseError("Bad line (missing ':'):\n" + line)
            else: # we are continuing 
                line = line.strip()
                if line:
                    rec[key] += " " + line.strip()
        self._dataDict = rec

    def _isContinuation(self, line):
        """Return True if line is a continuation line in the DCF file"""
        if re.match("^\s+", line):
            return True
        else:
            return False


class DCFParseError(Exception): pass
