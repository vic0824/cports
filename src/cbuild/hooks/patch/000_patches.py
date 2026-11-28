from cbuild.core import layout
from cbuild.util import patch


def invoke(pkg):
    if not pkg.srcdir.is_dir():
        return

    plist = []
    if pkg.patches_path.is_dir():
        plist += sorted(pkg.patches_path.glob("*"))
    # patches needed only by the prefix-less layout, applied after the
    # regular ones; kept apart so the /usr layout builds as before
    if layout.merged() and pkg.patches_nonux_path.is_dir():
        plist += sorted(pkg.patches_nonux_path.glob("*"))

    patch.patch(pkg, plist, stamp=True)
