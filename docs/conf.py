import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "JobShopLib"  # pylint: disable=invalid-name
copyright = "MIT License"  # pylint: disable=invalid-name, redefined-builtin
author = "Pablo Ariño"  # pylint: disable=invalid-name

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
add_module_names = False  # pylint: disable=invalid-name
python_use_unqualified_type_names = True  # pylint: disable=invalid-name

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "imported-members": True,
}

add_function_parentheses = True  # pylint: disable=invalid-name
modindex_common_prefix = ["job_shop_lib."]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"  # pylint: disable=invalid-name
html_static_path = ["_static"]
