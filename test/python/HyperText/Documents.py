__version__ = "$Revision: 1.4 $"[11:-4]

import HTML
import sys
from string import join

class Document:

    generator = HTML.META(name="generator",
                          content="HyperText package (Python)")
    DOCTYPE = HTML.DOCTYPE
    body_element = HTML.BODY

    def __init__(self, *content, **attrs):
	from HTML import HEAD, HTML
	self.doctype = self.DOCTYPE
	self.body = apply(self.body_element, content, attrs)
	self.head = HEAD(self.generator)
	if hasattr(self, 'style'): self.head.append(self.style)
	if hasattr(self, 'title'): self.head.append(self.title)
	self.html = HTML(self.head, self.body)
	self.setup()

    def setup(self): pass

    def append(self, *items): map(self.body.content.append, items)

    def __str__(self, indent=0, perlevel=2):
	return join([self.doctype.__str__(indent, perlevel),
		     self.html.__str__(indent, perlevel)], '')

    def writeto(self, fp=sys.stdout, indent=0, perlevel=2):
	self.doctype.writeto(fp, indent, perlevel)
	self.html.writeto(fp, indent, perlevel)


class FramesetDocument(Document):

    DOCTYPE = HTML.DOCTYPE_frameset
    body_element = HTML.FRAMESET


class CGIMixIn:

    def setup(self):
	self.content_type = "text/html"
	self.headers = []
	self.nobody = 0

    def _str_content_type(self):
	return 'Content-Type: %s\r\n\r\n' % self.content_type

    def __str__(self, indent=0, perlevel=2):
	s = self.headers[:]
	s.append(self._str_content_type())
	if not self.nobody:
	    s.append(self.doctype.__str__(indent, perlevel))
	    s.append(self.html.__str__(indent, perlevel))
	return join(s, '')

    def writeto(self, fp=sys.stdout, indent=0, perlevel=2):
	fp.writelines(self.headers)
	fp.write(self._str_content_type())
	if not self.nobody:
	    self.doctype.writeto(fp, indent, perlevel)
	    self.html.writeto(fp, indent, perlevel)


class HTTPMixIn(CGIMixIn):

    def setup(self):
	CGIMixIn.setup(self)
	if not hasattr(self, 'response'):
	    self.response = (200, 'Output follows')
	self.date = None

    http_response_str = "%s %s %s\r\nServer: %s %s\r\nDate: %s\r\n"

    def _str_http_response(self):
	if hasattr(self, 'request'):
	    apply(self.request.log_request, self.response)
	    return self.http_response_str \
		   % (self.request.request_version,
		      self.response[0],
		      self.response[1],
		      self.request.server_version,
		      self.request.sys_version,
		      self.date)
	else:
	    return self.http_response_str \
		   % ('HTTP/1.0',
		      self.response[0],
		      self.response[1],
		      "Dunno/0.0",
		      "BeatzMe/0.0",
		      self.date)

    def __str__(self, indent=0, perlevel=2):
	return join([self._str_http_response(),
		     CGIMixIn.__str__(self, indent, perlevel)], '')

    def writeto(self, fp=sys.stdout, indent=0, perlevel=2):
	fp.write(self._str_http_response())
	CGIMixIn.writeto(self, fp, indent, perlevel)




	
