"""Sphinx documentation configuration file."""

from datetime import datetime
import os

from ansys_sphinx_theme import (
    ansys_favicon,
    ansys_logo_white,
    ansys_logo_white_cropped,
    get_version_match,
    latex,
    watermark,
)
import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx.builders.latex import LaTeXBuilder

import ansys.tools.visualization_interface
from ansys.tools.visualization_interface import __version__

ansys.tools.visualization_interface.DOCUMENTATION_BUILD = True

LaTeXBuilder.supported_image_types = ["image/png", "image/pdf", "image/svg+xml"]

os.environ["PYANSYS_VISUALIZER_DOC_MODE"] = "true"
pyvista.BUILDING_GALLERY = True
os.environ["PYVISTA_BUILDING_GALLERY"] = "true"
pyvista.OFF_SCREEN = True


# Project information
project = "ansys-tools-visualization-interface"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", default="visualization-interface.tools.docs.pyansys.com")
switcher_version = get_version_match(__version__)

# Select desired logo, theme, and declare the html title
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "Visualization Interface Tool"
html_baseurl = f"https://{cname}/version/stable"

# specify the location of your github repo
html_context = {
    "github_user": "ansys",
    "github_repo": "ansys-tools-visualization-interface",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "logo": "pyansys",
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/ansys-tools-visualization-interface",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/ansys-tools-visualization-interface/discussions",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/ansys-tools-visualization-interface.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
    "ansys_sphinx_theme_autoapi": {
        "project": project,
    },
}

# Sphinx extensions
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_jinja",
    "numpydoc",
    "sphinx_gallery.gen_gallery",
    "pyvista.ext.viewer_directive",
    "ansys_sphinx_theme.extension.autoapi",
]

nbsphinx_execute = "always"
sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": ["../../examples"],
    # path where to save gallery generated examples
    "gallery_dirs": ["examples"],
    # Pattern to search for example files
    "filename_pattern": r"\.py",
    # Remove the "Download all examples" button from the top level gallery
    "download_all_examples": False,
    # Sort gallery example by file name instead of number of lines (default)
    # directory where function granular galleries are stored
    "backreferences_dir": None,
    # Modules for which function level galleries are created.  In
    "doc_module": "ansys-tools-visualization-interface",
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "ignore_pattern": "flycheck*",
    "thumbnail_size": (350, 350),
    "remove_config_comments": True,
    "show_signature": False,
}


# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.13", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pyvista": ("https://docs.pyvista.org/version/stable", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "pint": ("https://pint.readthedocs.io/en/stable", None),
    "beartype": ("https://beartype.readthedocs.io/en/stable/", None),
    "docker": ("https://docker-py.readthedocs.io/en/stable/", None),
    "pypim": ("https://pypim.docs.pyansys.com/version/stable", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    # "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# Configuration for Sphinx autoapi
suppress_warnings = ["autoapi.python_import_resolution", "design.grid", "config.cache"]

# Examples gallery customization
nbsphinx_execute = "always"

nbsphinx_epilog = """
----

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

nbsphinx_prolog = """

.. admonition:: Download this example

    Download this example as a `Jupyter Notebook <{cname_pref}/{ipynb_file_loc}>`_
    or as a `Python script <{cname_pref}/{py_file_loc}>`_.

----
""".format(
    cname_pref=f"https://{cname}/version/{switcher_version}",
    ipynb_file_loc="{{ env.docname }}.ipynb",
    py_file_loc="{{ env.docname }}.py",
)

typehints_defaults = "comma"
simplify_optional_unions = False

# additional logos for the latex coverpage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}

linkcheck_exclude_documents = ["index", "getting_started/local/index", "assets"]
linkcheck_ignore = [
    "https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyData.html#pyvista.PolyData",
    "https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.add_mesh.html#pyvista.Plotter.add_mesh",
    "https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.show.html#pyvista.Plotter.show",
    "https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Plotter.html#pyvista.Plotter",
    "https://docs.pyvista.org/api/core/_autosummary/pyvista.MultiBlock.html#pyvista.MultiBlock",
    "https://docs.pyvista.org/api/core/_autosummary/pyvista.UnstructuredGrid.html#pyvista.UnstructuredGrid",
    "https://docs.pyvista.org/api/plotting/_autosummary/pyvista.Actor.html#pyvista.Actor",
]


# -- Declare the Jinja context -----------------------------------------------
exclude_patterns = [
    "examples/**/*.ipynb",
    "examples/**/*.py",
    "examples/**/*.md5",
    "api/ansys/visualizer/index.rst",
]

BUILD_API = True
if not BUILD_API:
    exclude_patterns.append("autoapi")

BUILD_EXAMPLES = True
if not BUILD_EXAMPLES:
    exclude_patterns.append("examples/**")
    exclude_patterns.append("examples.rst")

jinja_contexts = {
    "main_toctree": {
        "build_api": BUILD_API,
        "build_examples": BUILD_EXAMPLES,
    }
}


def prepare_jinja_env(jinja_env) -> None:
    """Customize the jinja env.

    Notes
    -----
    See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment

    """
    jinja_env.globals["project_name"] = project


autoapi_prepare_jinja_env = prepare_jinja_env
