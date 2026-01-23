import os
import sys
# so accml_lib is found
sys.path.insert(0, os.path.abspath('../../'))

project = 'accml'
copyright = '2026, Helmholtz Zentrum Berlin'
author = 'Pierre Schnizer, Waheedullah Sulaiman Khail'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'sphinx.ext.autosummary',
    "sphinx.ext.todo",
    "sphinxcontrib.bibtex",
]
bibtex_bibfiles = ["refs.bib"]

# Optional formatting settings:
bibtex_default_style = "unsrt"   # or "alpha", "plain", etc.
bibtex_reference_style = "author_year"  # controls :cite: rendering style

autosummary_generate = True
autodoc_typehints = 'description'
html_theme = 'sphinx_rtd_theme'

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# optional: mock imports if your package has heavy optional deps
# autodoc_mock_imports = ['numpy', 'scipy', "lat2db", "acclerator-toolbox"]


# Intersphinx configuration: cross-reference external docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "accml_lib": ("https://python-accelerator-middle-layer.github.io/accml_lib/", None)
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#configuration

todo_include_todos = True
