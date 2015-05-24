__version__ = "$Revision: 1.2 $"[11:-4]

from SGML import Markup, Comment
from string import lower, join, replace

class XMLPI(Markup):

    attlist = {}
    defaults = {'version': '1.0'}
    attr_translations = {'id': 'ID',
                         'klass': 'class',
                         'label_for': 'for',
                         'http_equiv': 'http-equiv',
                         'accept_charset': 'accept-charset'}

    def __init__(self, **attr):
	self.dict = {}
	self.content = ()
	self.name = 'xml'
	self.dict.update(self.defaults)
	self.dict.update(attr)

    def __getitem__(self, k): return self.dict[k]

    def str_attribute(self, k):
        k2 = self.attr_translations.get(k, k)
	return '%s="%s"' % \
	       (k2, self.attlist.get(k, 1) and str(self[k]) or k2) \

    def str_attribute_list(self):
	return join(map(self.str_attribute, self.dict.keys()))

    start_tag_string = "<?%s %s"
    end_tag_string = " ?>\n"

    def start_tag(self):
	a = self.str_attribute_list()
	return self.start_tag_string % (self.name, a)

    def end_tag(self):
	return self.end_tag_string

