"""Import the Atik camera SDK, making sure its native library can be found.

The vendored ``libatikcameras.so`` (``vendor/atik/``) is not on the system library
path, and ``AtikSDK`` locates it via ``LD_LIBRARY_PATH`` when first imported.
Always import the SDK through this module::

    from numbat.atik import AtikSDK
"""

import os
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parents[2] / "vendor" / "atik"

if (_LIB_DIR / "libatikcameras.so").exists():
    _paths = os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep)
    if str(_LIB_DIR) not in _paths:
        os.environ["LD_LIBRARY_PATH"] = os.pathsep.join([str(_LIB_DIR), *filter(None, _paths)])

import AtikSDK  # noqa: E402

__all__ = ["AtikSDK"]
