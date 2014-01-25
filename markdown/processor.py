# -*- coding: utf-8 -*-

""" Because markdown just rocks!
    Get python-markdown2 from: https://github.com/trentm/python-markdown2

    @author  Alexander Dormann <alexander.dormann@30doradus.de>
    @date    16.10.2012
    @version 1.0.1-b2
    @package MarkdownProcessor
    @file    processor.py
"""

import re
import pkg_resources
from StringIO import StringIO

from trac.core import implements
from trac.wiki.macros import WikiMacroBase
from trac.wiki.formatter import Formatter
from trac.web.chrome import ITemplateProvider

import markdown2

#pylint: disable=abstract-method

# links, autolinks, and reference-style links
LINK = re.compile(r'(\]\()([^) ]+)([^)]*\))|(<)([^>]+)(>)|(\n\[[^]]+\]: *)([^ \n]+)(.*\n)')
HREF = re.compile(r'href=[\'"]?([^\'" ]*)', re.I)

# set some cool extras:
MD_EXTRAS = [
    "code-friendly",      # ignore _ + __ formattings
    "fenced-code-blocks", # syntax highlighting!
    "header-ids",         # explains itself by name
    "smarty-pants",       # typo goodness (cf. http://daringfireball.net/projects/smartypants)
    "wiki-tables",         # render trac-wiki tables within md macro
]

class mdMacro(WikiMacroBase):
    """enables the markdown processor macro."""
    implements(ITemplateProvider)

    def expand_macro(self, formatter, name, content):

        env = formatter.env
        _abs = env.abs_href.base
        _abs = _abs[:len(_abs) - len(env.href.base)]
        f = Formatter(formatter.env, formatter.context)

        def convert_links(m):
            pre, target, suf = filter(None, m.groups())
            out = StringIO()
            f.format(target, out)
            url = re.search(HREF, out.getvalue()).groups()[0]
            # Trac creates relative links, which Markdown won't touch inside
            # <autolinks> because they look like HTML
            if pre == '<' and url != target:
                pre += _abs
            return pre + str(url) + suf

        # autolink http:// n stuff
        autolinked_content = re.sub(LINK, convert_links, content)
        # convert to markdown
        html = markdown2.markdown(autolinked_content, extras=MD_EXTRAS)
        return html

    # ITemplateProvider methods
    def get_htdocs_loc(self):
        return pkg_resources.resource_filename('markdown', 'htdocs')
    htdocs_loc = property(get_htdocs_loc)

    def get_htdocs_dirs(self):
        return [('markdown', self.htdocs_loc)]

    def get_templates_dirs(self):
        return []
