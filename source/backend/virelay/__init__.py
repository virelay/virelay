"""A package that contains the ViRelAy application, which to view source-data, attributions, clusterings, and (t-SNE-)embeddings."""

try:
    from virelay.version import version as VERSION
except ModuleNotFoundError:
    VERSION = 'unknown'

__version__ = VERSION
"""Contains the version of the ViRelAy application."""

__author__ = 'Christopher J. Anders, David Neumann, Talmaj Marinč, Sebastian Lapuschkin, and Pattarawat Chormai'
"""Contains the author of the ViRelAy application."""

__license__ = 'AGPL-3.0-or-later'
"""Contains the license of the ViRelAy application."""

__copyright__ = 'Copyright © 2024, The ViRelAy Project'
"""Contains the copyright of the ViRelAy application."""
