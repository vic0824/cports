"""Target filesystem layout.

By default packages are installed with the /usr prefix. Setting the
CBUILD_TARGET_PREFIX environment variable to "/" switches the *target*
layout to a prefix-less one (/bin, /lib, /include, /share).

Only the layout of the packages being produced changes; the build root
the packages are built in keeps its own layout, so absolute paths of
tools inside the build root must not go through this module.
"""

import os
import pathlib

_prefix = os.environ.get("CBUILD_TARGET_PREFIX", "/usr").rstrip("/")

if _prefix not in ("", "/usr"):
    raise RuntimeError("CBUILD_TARGET_PREFIX must be '/' or '/usr'")


def merged():
    """Whether the target layout has no /usr."""
    return _prefix == ""


def prefix():
    """The install prefix, as passed to build systems."""
    return _prefix or "/"


def path(sub=""):
    """Absolute target path of a prefix-relative directory."""
    return f"{_prefix}/{sub}" if sub else prefix()


# Directories of package-provided defaults that would otherwise sit in
# /usr/lib with overrides in /etc. With no /usr there is a single location
# for each of them, in /etc, so there is no default/override cascade.
ETC_DIRS = (
    "binfmt.d",
    "dinit.d",
    "modprobe.d",
    "modules-load.d",
    "sysctl.d",
    "sysusers.d",
    "tmpfiles.d",
)


def _rel(s):
    if s == "usr":
        return "."
    if not s.startswith("usr/"):
        return s
    s = s[4:]
    if s.startswith("lib/"):
        d, sep, rest = s[4:].partition("/")
        if d in ETC_DIRS:
            return f"etc/{d}{sep}{rest}"
    return s


def rel(p):
    """Translate a destdir-relative path written for the /usr layout."""
    if not merged():
        return p
    if isinstance(p, pathlib.PurePath):
        return type(p)(_rel(os.fspath(p)))
    return _rel(p)


class DestPath(pathlib.PosixPath):
    """A destdir root that translates /usr-relative paths joined to it.

    Templates and hooks address files as destdir / "usr/bin/foo". With a
    prefix-less target layout the same expression resolves to "bin/foo".
    Only the root translates; derived paths are plain paths.
    """

    def with_segments(self, *segs):
        return pathlib.PosixPath(*segs)

    def _plain(self):
        return pathlib.PosixPath(self)

    def __truediv__(self, key):
        return self._plain() / rel(key)

    def joinpath(self, *segs):
        if segs:
            segs = (rel(segs[0]), *segs[1:])
        return self._plain().joinpath(*segs)

    def glob(self, pattern, **kw):
        return self._plain().glob(rel(pattern), **kw)

    def rglob(self, pattern, **kw):
        return self._plain().rglob(rel(pattern), **kw)

    @property
    def parent(self):
        return self._plain().parent
