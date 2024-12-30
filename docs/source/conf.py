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

pygments_style = "friendly"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"  # pylint: disable=invalid-name
html_css_files = ["custom.css"]
templates_path = ["_templates"]

html_logo = "images/logo_no_bg_resized_fixed.png"

html_theme_options = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/Pabloo22/job_shop_lib",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,  # noqa: E501
            "class": "",
        },
    ],
}
