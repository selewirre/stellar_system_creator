# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------
import pkg_resources

project = 'Stellar System Creator'
copyright = '2021, Selewirre Iskvary'
author = 'Selewirre Iskvary'

# The full version, including alpha/beta/rc tags
release = '0.1.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
 'sphinx_search.extension',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
# html_theme = 'sphinx_rtd_theme'
html_theme = 'sphinx_material'  # https://bashtage.github.io/sphinx-material/index.html

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

image_filename = pkg_resources.resource_filename('stellar_system_creator', 'gui/logo.ico')
html_logo = image_filename

html_show_sourcelink = False

# for rtd theme
# html_theme_options = {
#     'style_external_links': True,
#     'style_nav_header_background': 'red',
#     # Toc options
#     'sticky_navigation': True,
#     'navigation_depth': -1}

# for material theme
html_theme_options = {
    'nav_title': project,
    # 'theme_color': '4D1A7F',
    'color_primary': 'indigo',
    'color_accent': 'red',
    'globaltoc_depth': 2,
}

html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

