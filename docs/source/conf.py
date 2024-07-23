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
    "undoc-members": True,
    "show-inheritance": True,
    "imported-members": False,
    "special-members": "__call__",
}
add_function_parentheses = True  # pylint: disable=invalid-name
modindex_common_prefix = ["job_shop_lib."]
smartquotes = False  # pylint: disable=invalid-name

autodoc_typehints = "description"
autodoc_typehints_format = "short"

napoleon_include_init_with_doc = True  # pylint: disable=invalid-name
napoleon_preprocess_types = True  # pylint: disable=invalid-name

napoleon_type_aliases = {
    "`Dispatcher`": ":class:`~job_shop_lib.dispatching.Dispatcher`",
    "`DispatcherObserver`": (
        ":class:`~job_shop_lib.dispatching.DispatcherObserver`"
    ),
    "`FeatureType`": (
        ":class:`~job_shop_lib.dispatching.feature_observers.FeatureType`"
    ),
    "`GraphUpdater`": (
        ":class:`~job_shop_lib.graphs.graph_updaters.GraphUpdater`"
    ),
    "`IsCompletedObserver`": (
        ":class:`~job_shop_lib.dispatching.feature_observers"
        ".IsCompletedObserver`"
    ),
    "`JobShopGraph`": ":class:`~job_shop_lib.graphs.JobShopGraph`",
    "`Operation`": ":class:`~job_shop_lib.Operation`",
    "`ScheduledOperation`": ":class:`~job_shop_lib.ScheduledOperation`",
    "`NodeType`": ":class:`~job_shop_lib.graphs.NodeType`",
    "`ValidationError`": ":class:`~job_shop_lib.exceptions.ValidationError`",
    "`UninitializedAttributeError`": (
        ":class:`~job_shop_lib.exceptions.UninitializedAttributeError`"
    ),
    "`remove_completed_operations`": (
        ":func:`~job_shop_lib.graphs.graph_updaters"
        ".remove_completed_operations`"
    ),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"  # pylint: disable=invalid-name
html_static_path = ["_static"]
html_css_files = ["custom.css"]
templates_path = ["_templates"]

html_logo = "images/logo_no_bg_resized_fixed.png"
