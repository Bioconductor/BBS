__version__ = "$Revision: 1.1 $"[11:-4]

from sys import stdout
from string import lower, join, replace

class Markup:

    content_model = 1

    def __init__(self, name, *content):
	self.name = name
	self.dict = {}
	self.content = list(content)

    start_tag_string = "<!%s "

    def append(self, *items): map(self.content.append, items)

    def start_tag(self): return self.start_tag_string % self.name

    def end_tag(self):	return ">\n"

    def writeto(self, fp=stdout, indent=0, perlevel=0):
	fp.write(self.start_tag())
	for c in self.content:
	    if hasattr(c, 'writeto'):
		getattr(c, 'writeto')(fp, indent+perlevel, perlevel)
	    else:
		fp.write(str(c))
	fp.write(self.end_tag())

    def __str__(self, indent=0, perlevel=0):
	# we don't actually indent here, it's for later.
	c = map(str, self.content)
	return join([self.start_tag()]+c+[self.end_tag()],'')


def Comment(*comment): return apply(Markup, ('--',)+comment+(' --',))

