# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

# sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../../drive/'))
sys.path.insert(0, os.path.abspath('../'))

project = 'DRIVE'
copyright = '2023, James Baker, Hung-Hsin Chen, Jennifer Piper-Below, David Samuels'
author = 'James Baker, Hung-Hsin Chen, Jennifer Piper-Below, David Samuels'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
master_doc = 'index'
extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
