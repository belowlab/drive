# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

# import drive


project = "DRIVE"
copyright = "2023, James Baker, Hung-Hsin Chen, David Samuels, Jennifer Piper-Below"
author = "James Baker, Hung-Hsin Chen, David Samuels, Jennifer Piper-Below"
release = "2.7.15a1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


sys.path.insert(0, os.path.abspath("../../src/"))
sys.path.insert(0, os.path.abspath("../../"))

github_url = "https://github.com/belowlab/drive"

extensions = [
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    'sphinx.ext.todo',
    'sphinx.ext.autosectionlabel'
    # 'sphinxcontrib_autodocgen'
]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
master_doc = "index"

html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/belowlab/drive",
    "use_repository_button": True,
    "home_page_in_toc": True,
}
html_title = "DRIVE"
