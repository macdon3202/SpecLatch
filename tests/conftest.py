"""Windows temporary-file cleanup compatibility for gltest."""
import os
import sys
if sys.platform == "win32":
    _unlink = os.unlink
    def safe_unlink(path, *args, **kwargs):
        try:
            return _unlink(path, *args, **kwargs)
        except PermissionError:
            if os.path.basename(path).startswith("tmp"):
                return None
            raise
    os.unlink = safe_unlink
