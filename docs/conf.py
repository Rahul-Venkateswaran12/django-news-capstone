# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import django

# Path: add project root so autodoc can import your app
sys.path.insert(0, os.path.abspath('..') )     # if docs is at project/docs then adjust if needed
# If docs is in project/docs and your django settings are in project/news_project/settings.py, then:
sys.path.insert(0, os.path.abspath('..'))  # now Python can import news and news_project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_project.settings')
django.setup()


project = 'News Application'
copyright = '2025, Rahul Venkateswaran'
author = 'Rahul Venkateswaran'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
