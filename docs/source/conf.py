"""Represents the configuration for Sphinx, which is executed at build time and can be used to configure Sphinx's input and output behavior."""

# pylint: disable=invalid-name

import os
import sys
import inspect
from types import ModuleType
from typing import Any, Iterator, Literal
from collections.abc import Sequence
from subprocess import run, CalledProcessError

from sphinx.application import Sphinx
from pybtex.database import Entry
from pybtex.plugin import register_plugin
from pybtex.style.labels import BaseLabelStyle
from pybtex.style.formatting.plain import Style as PlainStyle


class AuthorYearLabelStyle(BaseLabelStyle):
    """Represents a citation label style, which uses the format "[<first-author> et al., <year>]"."""

    def format_labels(self, sorted_entries: list[Entry]) -> Iterator[str]:
        """Formats the labels of all bibliography entries.

        Args:
            sorted_entries (list[Entry]): The sorted list of bibliography entries.

        Yields:
            str: Yields the formatted labels of all bibliography entries.
        """

        for entry in sorted_entries:
            yield f'[{entry.persons["author"][0].last_names[0]} et al., {entry.fields["year"]}]'


class AuthorYearStyle(PlainStyle):
    """Represents a custom bibliography style, which uses the citation label format "[<first-author> et al., <year>]"."""

    default_label_style: str | type = AuthorYearLabelStyle
    """The label style to use for the bibliography entries."""


def setup(app: Sphinx) -> None:
    """Is invoked by Sphinx, when this build configuration file is executed.

    Args:
        app (Sphinx): The Sphinx application.
    """

    # Sets the name of the directory into which generated documentation files are to be written and makes sure that the
    # directory exists (this is done by signing up for the config-inited event, which is emitted when the configuration
    # has been fully initialized)
    app.add_config_value('generated_path', '_generated', 'env')
    app.connect(
        'config-inited',
        lambda app, _: os.makedirs(os.path.join(app.srcdir, app.config.generated_path), exist_ok=True)
    )


def get_latest_git_tag() -> str:
    """Retrieves the latest Git tag in the source code repository.

    Returns:
        str: Returns the name of the latest Git tag in the source code repository. If no tags are available, then "master" is returned.
    """

    # Tries to get the most recent tag in the source code repository using the git describe command, which returns the
    # closest tag that can be reached from the specified revision, which in this case is the latest commit on master,
    # if no tags are available, then "master" is returned as a fallback
    try:
        return run(
            ['git', 'describe', '--tags', 'HEAD'],
            capture_output=True,
            check=True,
            text=True
        ).stdout[:-1]
    except CalledProcessError:
        return 'master'


def linkcode_resolve(domain: Literal['py', 'c', 'cpp', 'javascript'], info: dict[str, str]) -> str | None:
    """Determines the URL to the source code corresponding to the object in the specified domain with the provided information. This function was
    adapted from https://gist.github.com/nlgranger/55ff2e7ff10c280731348a16d569cb73.

    Args:
        domain (Literal['py', 'c', 'cpp', 'javascript']): Specified the language domain the object is in. Can be one of "py", "c", "cpp", or
            "javascript".
        info (dict[str, str]): A dictionary, which contains further information about the object for which the URL is to be retrieved. Depending on
            the domain, the following keys are guaranteed to be present:
             - domain is "py":
               - "module", which contains the name of the module.
               - "fullname", which contains the full name of the object.
             - domain is "c":
               - "names", which contains a list of names for the object.
             - domain is "cpp":
               - "names", which contains a list of names for the object.
             - domain is "javascript":
               - "object", which is the name of the object.
               - "fullname", which is the name of the item.

    Returns:
        str | None: Returns the URL of the source code corresponding to the specified object. If no URL is available, then None is returned.
    """

    # We are only interested in Python source code URLs
    if domain != 'py' or 'module' not in info or 'fullname' not in info:
        return None

    # Gets the module in which the object resides for which the source code URL is to be retrieved
    module: ModuleType | None = sys.modules.get(info['module'])
    if module is None:
        return None

    # Gets the object for which the source code URL is to be retrieved
    name_components = info['fullname'].split('.')
    if not name_components:
        return None
    object_to_get_url_for: ModuleType | type[Any] = module
    for name_component in name_components:
        try:
            object_to_get_url_for = getattr(object_to_get_url_for, name_component)
        except AttributeError:
            return None

    # Gets the absolute path to the source code file that contains the object
    object_file_path: str | None = inspect.getsourcefile(object_to_get_url_for)
    if object_file_path is None:
        return None

    # The path to the source code file is absolute, so it must be converted to a path relative to the top module's path (this should always be the
    # virelay module; example: source code file path: /a/b/c/virelay/d/e.py, top module path: /a/b/c/virelay, and what we need is virelay/d/e.py); the
    # path returned by the __file__ attribute of the top module points to the module's __init__.py file, e.g., /a/b/c/virelay/__init__.py, so we need
    # to remove the __init__.py part to get the top module's path; then, we also need to remove the directory that the top module is contained in,
    # e.g., /a/b/c; this is needed because the function that turns the absolute into a relative path removes the common prefix of the two paths, which
    # would mean that we would end up with d/e.py instead of virelay/d/e.py
    module_hierarchy = info['module'].split('.')
    if not module_hierarchy:
        return None
    top_module_name = module_hierarchy[0]
    top_module = sys.modules.get(top_module_name)
    if top_module is None or top_module.__file__ is None:
        return None
    top_module_path = os.path.abspath(os.path.join(os.path.dirname(top_module.__file__), '..'))
    object_file_path = os.path.relpath(object_file_path, top_module_path)

    # Retrieves the line number at which the object's definition starts and the line number where it ends
    try:
        source, line_number = inspect.getsourcelines(object_to_get_url_for)
        line_start, line_stop = line_number, line_number + len(source) - 1
    except OSError:
        return None

    # Composes the URL to the source code file on GitHub and returns it
    return f'https://github.com/virelay/virelay/blob/{LATEST_GIT_TAG}/{object_file_path}#L{line_start}-L{line_stop}'


# Sets the basic project information
project = 'ViRelAy'
project_copyright = '2024, ViRelAy'
author = 'ViRelAy Contributors'

# Specifies the Sphinx extensions that are used by this documentation
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.linkcode',
    'sphinx.ext.imgmath',
    'sphinx.ext.extlinks',
    'sphinx_rtd_theme',
    'sphinx_copybutton',
    'sphinxcontrib.datatemplates',
    'sphinxcontrib.bibtex'
]

# Specifies the path that contains extra templates
templates_path = ['_templates']

# Specifies a list of patterns, relative to source directory, that match files and directories to ignore when looking
# for source files, in this case, nothing needs to be excluded
exclude_patterns: Sequence[str] = []

# Configures the theme that is used for the HTML pages
html_theme = 'sphinx_rtd_theme'
html_favicon = '_static/favicon.ico'
html_static_path = ['_static']

# Configures the Sphinx plugin, which adds a copy button to code blocks
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOT"

# Configures the Sphinx plugin, which allows BibTeX citations to be inserted into documentation
bibtex_bibfiles = ['bibliography.bib']
bibtex_default_style = 'author_year_style'
bibtex_reference_style = 'author_year'

# Configures the Sphinx plugin, which shortens external Links to the GitHub repository (also, a custom formatting style
# is registered with Pybtex, which customizes the citation labels to use the format "[<first-author> et al., <year>]")
LATEST_GIT_TAG = get_latest_git_tag()
extlinks = {
    'repo': (
        f'https://github.com/virelay/virelay/blob/{LATEST_GIT_TAG}/%s',
        '%s'
    )
}
register_plugin('pybtex.style.formatting', 'author_year_style', AuthorYearStyle)
