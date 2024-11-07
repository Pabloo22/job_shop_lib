import os
import sys

from job_shop_lib import __version__

version = __version__  # pylint: disable=invalid-name

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
# release = "1.0.0-beta.1"  # pylint: disable=invalid-name

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "nbsphinx",
    "nbsphinx_link",
    "sphinx.ext.doctest",
    "myst_parser",
    "sphinx.ext.autodoc.typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_*.py"]
add_module_names = False  # pylint: disable=invalid-name
python_use_unqualified_type_names = True  # pylint: disable=invalid-name
autosummary_generate = True  # pylint: disable=invalid-name
autosummary_generate_overwrite = True  # pylint: disable=invalid-name

autodoc_mock_imports = ["ortools"]
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "show-inheritance": True,
    "imported-members": False,
    "special-members": "__call__",
    "exclude-members": "__weakref__, __dict__, __module__",
}
add_function_parentheses = True  # pylint: disable=invalid-name
modindex_common_prefix = ["job_shop_lib."]
smartquotes = False  # pylint: disable=invalid-name

autodoc_typehints = "description"
autodoc_typehints_format = "short"

napoleon_include_init_with_doc = True  # pylint: disable=invalid-name
napoleon_preprocess_types = True  # pylint: disable=invalid-name


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"  # pylint: disable=invalid-name
html_css_files = ["custom.css"]
templates_path = ["_templates"]

html_logo = "images/logo_no_bg_resized_fixed.png"
