# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(1, os.path.abspath('../../gemdeps'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'gemdeps'
copyright = u'2016, Balasankar C'
author = u'Balasankar C'

version = u'1.0'
release = u'1.0'

language = None

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = True

html_theme = 'alabaster'

html_static_path = ['_static']

htmlhelp_basename = 'gemdepsdoc'

latex_elements = {
}

latex_documents = [
    (master_doc, 'gemdeps.tex', u'gemdeps Documentation',
     u'Balasankar C', 'manual'),
]

man_pages = [
    (master_doc, 'gemdeps', u'gemdeps Documentation',
     [author], 1)
]


texinfo_documents = [
    (master_doc, 'gemdeps', u'gemdeps Documentation',
     author, 'gemdeps', 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_exclude_files = ['search.html']

intersphinx_mapping = {'https://docs.python.org/': None}
