"""Target filesystem layout, for templates.

Templates may only import from cbuild.util; this re-exports the parts of
cbuild.core.layout that a template needs to tell the layouts apart.
"""

from cbuild.core.layout import merged, path, prefix

__all__ = ["merged", "path", "prefix"]
