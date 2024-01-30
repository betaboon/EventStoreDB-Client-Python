# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import importlib
import inspect
import pathlib

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "EventstoreDB Client Python"
copyright = "2024, betaboon"  # noqa: A001
author = "betaboon"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # stock extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.linkcode",
    "sphinx.ext.napoleon",
    # third party extensions
    "autoapi.extension",
    "myst_parser",
    "sphinx_copybutton",
]


# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_class_signature = "separated"
autodoc_typehints = "description"
autodoc_typehints_format = "short"


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
}


# -- Options for linkscode ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#configuration
# adapted from: https://github.com/readthedocs/sphinx-autoapi/issues/202
repository_url = "https://github.com/betaboon/EventStoreDB-Client-Python/blob/main"
python_import_name = "eventstoredb"


def linkcode_resolve(domain: str, info: dict[str, str]) -> str | None:
    if domain != "py":
        return None

    mod = importlib.import_module(info["module"])
    if "." in info["fullname"]:
        objname, attrname = info["fullname"].split(".")
        obj = getattr(mod, objname)
        try:
            # object is a method of a class
            obj = getattr(obj, attrname)
        except AttributeError:
            # object is an attribute of a class
            return None
    else:
        obj = getattr(mod, info["fullname"])

    obj = inspect.unwrap(obj)

    try:
        file = inspect.getsourcefile(obj)
        lines = inspect.getsourcelines(obj)
    except TypeError:
        return None

    if not file:
        return None

    docs_path = pathlib.Path(__file__).parent
    repo_path = docs_path.parent
    file_path = pathlib.Path(file).relative_to(repo_path)

    if not str(file_path).startswith(f"{python_import_name}/"):
        return None

    line_start = lines[1]
    line_end = lines[1] + len(lines[0]) - 1

    return f"{repository_url}/{file_path}#L{line_start}-L{line_end}"


# -- Options for autoapi -----------------------------------------------------
# https://sphinx-autoapi.readthedocs.io/en/latest/reference/config.html

autoapi_type = "python"
autoapi_add_toctree_entry = False

autoapi_root = "api"
autoapi_dirs = ["../eventstoredb"]

autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]


# -- Options for myst-parser -------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

language = "en"

html_static_path = ["_static"]

html_theme = "furo"
html_title = "EventstoreDB Client Python"

html_theme_options = {
    "source_repository": "https://github.com/betaboon/EventStoreDB-Client-Python",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/betaboon/EventStoreDB-Client-Python",
            "html": (
                """<svg stroke="currentColor" fill="currentColor" """
                """stroke-width="0" viewBox="0 0 16 16">"""
                """<path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 """
                """3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-"""
                """.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94"""
                """-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23."""
                """82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-"""
                """.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36"""
                """-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27"""
                """.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.1"""
                """6 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-"""
                """3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 """
                """0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8"""
                """-8-8z"></path></svg>"""
            ),
            "class": "",
        },
    ],
}
