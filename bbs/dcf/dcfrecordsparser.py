import unittest
import tempfile
import urllib2
import re
import time

"""
This file contains two main classes: DcfRecordParser 
and DcfRecordsParser. DcfRecordParser can parse a single
DCF record; DcfRecordsParser separates multiple records 
and hands them off to DcfRecordParser. Unlike the previous
implementation of getNextDcfVal() in bbs.parse, this can
handle continuation lines (newlines are stripped from the
result).

To take advantage of this, current code like this:

    summary_file = os.path.join(buildsrc_path, summary_file0 % 'buildsrc')
    dcf = open(summary_file, 'r')
    status = bbs.parse.getNextDcfVal(dcf, 'Status')

...should be changed to:


from bbs.dcf.dcfrecordsparser import DcfRecordsParser
    summary_file = os.path.join(buildsrc_path, summary_file0 % 'buildsrc')
    dcf = open(summary_file, 'r')
    dcfrecords = DcfRecordsParser(dcf)
    status = dcfrecords.getNextDcfVal('Status')

IMPORTANT: code that switches to use this class should also
be sure and catch the relevant exception which is
bbs.dcf.dcfrecordsparser.DCFParseError. Otherwise your code
is still looking for an exception which will not be thrown
and if not caught, this exception could disrupt a build.

"""

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
        self.keys = []
        self._parseRecord()


    def __str__(self):
        s = ""
        for key in self.keys:
            s += "%s: %s\n" % (key, self._dataDict[key])
        return s

    def getValue(self, field, full_line=False):
        """Return the value associated with the specified field.

        If no such value, raise a KeyError.
        """
        val = self._dataDict[field]
        if (full_line):
            return val
        else:
            return val.split()[0]


    def _parseRecord(self):
        """Parse a single DCF record (group of key/value lines)."""
        rec = {}
        key = None
        for line in self.file:
            if (line.strip().startswith("#")):
                continue
            if not self._isContinuation(line):
                pos = line.find(':')
                if pos > 0:
                    key = line[0:pos]
                    val = line[pos+1:]
                    rec[key] = val.strip()
                    self.keys.append(key)
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





class DcfRecordsParser:
    def __init__(self, iterable):
        self.iterable = iterable
        self.last_record = None
        self.last_field = None
        self.it = iter(self.iterable)
        self.atEnd = False

    def _getNextRecord(self):
        lines = []
        while True:
            try:
                line = self.it.next()
            except StopIteration:
                if len(lines) <= 0:
                    self.atEnd = True
                break
            if line == "\n" or line == "":
                break
            for subline in line.split("\n"):
                if subline:
                    lines.append(subline)
        self.last_record = DcfRecordParser(lines)
        return self.last_record

    def _readNext(self, field, full_line):
        record = self._getNextRecord()
        self.last_field = field
        try:
            return record.getValue(field, full_line)
        except KeyError:
            return None

    def getNextDcfVal(self, field, full_line=False):
        if self.atEnd:
            return None
        if (self.last_record is None):
            self._getNextRecord()
            if (self.last_record is None):
                return None
        while (field not in self.last_record.keys):
            self._getNextRecord()
            if (self.atEnd):
                return None

        keys = self.last_record.keys
        if self.last_field in keys:
            pos = keys.index(self.last_field) +1
        else:
            pos = 0
        slice = keys[pos:]
        if field in slice:
            self.last_field = field
            return(self.last_record.getValue(field, full_line))
        else:
            return(self._readNext(field, full_line))

if __name__ == '__main__':



  def OLDgetNextDcfVal(dcf, field, full_line=False):
    if full_line:
        val_regex = '\\S.*'
    else:
        val_regex = '\\S+'
    regex = '%s\\s*:\\s*(%s)' % (field, val_regex)
    p = re.compile(regex)
    val = None
    for line in dcf:
        if not line.startswith(field):
            continue
        m = p.match(line)
        if m:
            val = m.group(1)
        else:
            val = ""
        break
    return val;



  class DcfRecordsParserTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def m(self, actual, expected):
        return("expected %s, got %s" % (expected, actual))


    def test_lineWithExtraColon(self):
        c = DcfRecordsParser(["A: a1:something", "B: b1", "\n", "A: a2", "B: b2"])
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a1:something", self.m(res0, "a1:something")

    def test_StayInFirstRecord(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n", "A: a2", "B: b2"])
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a1", self.m(res0, "a1")
        res1 = c.getNextDcfVal("B", True)
        assert res1 == "b1", self.m(res1, "b1")

    def test_HandleContinuationLine(self):
        c = DcfRecordsParser(["A: a long\n value", "B: b1\n continues"])
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a long value", self.m(res0, "a long value")
        res1 = c.getNextDcfVal("B", True)
        assert res1 == "b1 continues", self.m(res1, "b1 continues")

    def test_twoInARow(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n", "A: a2", "B: b2"])
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a1", self.m(res0, "a1")
        res1 = c.getNextDcfVal("A", True)
        assert res1 == "a2", self.m(res1, "a2")

    def test_SkipToNextRecord(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n", "A: a2", "B: b2"])
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a1", self.m(res0, "a1")
        res1 = c.getNextDcfVal("A", True)
        assert res1 == "a2", self.m(res1, "a2")
        res2 = c.getNextDcfVal("B", True)
        assert res2 == "b2", self.m(res2, "b2")
        res3 = c.getNextDcfVal("Foo", True)
        assert res3 is None, self.m(res3, None)
        res4 = c.getNextDcfVal("B", True)
        assert res4 is None, self.m(res4, None)

    def test_MissingFieldAdvancesPointerToEnd(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n", "A: a2", "B: b2"])
        res0 = c.getNextDcfVal("Foo", True)
        assert res0 == None, self.m(res0, None)
        res1 = c.getNextDcfVal("A", True)
        assert res1 == None, self.m(res1, None)

    def test_WithDiskFile(self):
        t = tempfile.mkstemp()
        f = open(t[1], "w")
        f.write("A: a1 bla\nB: a long\n value\n\nA: a2\nB: B2")
        f.close()
        f = open(t[1])
        c = DcfRecordsParser(f)
        res0 = c.getNextDcfVal("A")
        assert res0 == "a1", self.m(res0, "a1")
        res1 = c.getNextDcfVal("B", True)
        assert res1 == "a long value", self.m(res1, "a long value")
        res2 = c.getNextDcfVal("B", True)
        assert res2 == "B2", self.m(res2, "B2")

    def test_WithUrl(self):
        t = tempfile.mkstemp()
        f = open(t[1], "w")
        f.write("A: a1\nB: a long\n value\n\nA: a2\nB: B2")
        f.close()
        url = "file://%s" % t[1]
        urlobj = urllib2.urlopen(url)
        c = DcfRecordsParser(urlobj)
        res0 = c.getNextDcfVal("A", True)
        assert res0 == "a1", self.m(res0, "a1")
        res1 = c.getNextDcfVal("B", True)

    def test_WithFull_LineFalse(self):
        c = DcfRecordsParser(["A: a1 bla", "B: b1 bla", "\n", "A: a2 bla", "B: b2\tbla"])
        res0 = c.getNextDcfVal("B")
        assert res0 == "b1", self.m(res0, "b1")
        res1 = c.getNextDcfVal("B")
        assert res1 == "b2", self.m(res1, "b2")

    def test_withARealFile(self):
        url = "http://bioconductor.org/packages/2.11/bioc/src/contrib/PACKAGES"
        urlobj = urllib2.urlopen(url)
        c = DcfRecordsParser(urlobj)
        while True:
            res0 = c.getNextDcfVal("Package")
            if res0 == "Biobase" or res0 is None:
                break
        if res0 is None:
            fail("Could not find Biobase")
        res1 = c.getNextDcfVal("License")
        assert res1 == "Artistic-2.0", self.m(res1, "Artistic-2.0")
        res2 = c.getNextDcfVal("ABogusField")
        assert res2 is None, self.m(res2, None)

    def test_SkipToNextRecord2(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n", "C: c1"])
        res0 = c.getNextDcfVal("C", True)
        assert res0 == "c1", self.m(res0, "c1")

    def test_withExtraDelimiters(self):
        c = DcfRecordsParser(["A: a1", "B: b1", "\n\n\n\n", "\n", "C: c1"])
        res0 = c.getNextDcfVal("C", True)
        assert res0 == "c1", self.m(res0, "c1")


  class DcfRecordsParserPerformanceTest():

      def test0(self):
          start_time = time.time()
          recs = ["A: a1:something", "B: b1", "\n", "A: a2", "B: b2"]
          c = DcfRecordsParser(recs)
          res0 = c.getNextDcfVal("A", True)
          assert res0 == "a1:something", self.m(res0, "a1:something")
          elapsed_time0 = time.time() - start_time
          print("test0: elapsed_time0: %.6f" % elapsed_time0)
          start_time = time.time()
          OLDgetNextDcfVal(recs, "A")
          elapsed_time1 = time.time() - start_time
          print("test0: elapsed_time1: %.6f" % elapsed_time1)

      def test1(self):
          print()
          url = "http://bioconductor.org/packages/2.11/bioc/src/contrib/PACKAGES"
          urlobj = urllib2.urlopen(url)
          start_time = time.time()
          c = DcfRecordsParser(urlobj)
          while True:
              res0 = c.getNextDcfVal("Package")
              if res0 == "Biobase" or res0 is None:
                  break
          if res0 is None:
              fail("Could not find Biobase")
          res1 = c.getNextDcfVal("License")
          res2 = c.getNextDcfVal("ABogusField")
          elapsed_time0 = time.time() - start_time
          print("test1: elapsed_time0: %.6f" % elapsed_time0)

          urlobj = urllib2.urlopen(url)
          start_time = time.time()
          OLDgetNextDcfVal(urlobj, "Package")
          while True:
              res0 = OLDgetNextDcfVal(urlobj, "Package")
              if res0 == "Biobase" or res0 is None:
                  break
          if res0 is None:
              fail("Could not find Biobase")
          res1 = OLDgetNextDcfVal(urlobj, "License")
          res2 = OLDgetNextDcfVal(urlobj, "ABogusField")
          elapsed_time1 = time.time() - start_time
          print("test1: elapsed_time1: %.6f" % elapsed_time1)



      def test2(self):
          print()
          recs = ["A: a1", "B: b1", "\n", "A: a2", "B: b2"]
          start_time = time.time()
          c = DcfRecordsParser(recs)
          res0 = c.getNextDcfVal("A", True)
          res1 = c.getNextDcfVal("B", True)
          elapsed_time0 = time.time() - start_time
          print("test2: elapsed_time0: %.6f" % elapsed_time0)

          start_time = time.time()
          OLDgetNextDcfVal(recs, "A", True)
          OLDgetNextDcfVal(recs, "B", True)
          elapsed_time1 = time.time() - start_time
          print("test2: elapsed_time1: %.6f" % elapsed_time1)




  def suite():
    suite = unittest.makeSuite(DcfRecordsParserTest,'test')
    return(suite)




  runner = unittest.TextTestRunner()
  runner.run(suite())

  pt = DcfRecordsParserPerformanceTest()
  pt.test0()
  pt.test1()
  pt.test2()
