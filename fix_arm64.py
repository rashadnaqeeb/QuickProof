"""Make accessible_output2 work on Windows on ARM (ARM64 Python).

accessible_output2 ships x64-only DLLs, so on an ARM64 build of Python the
NVDA output fails to load and Auto() crashes, which kills QuickProof at
startup with no visible error. This script fixes that in place:

1. Downloads the official NVDA controller client from NV Access and installs
   its native ARM64 nvdaControllerClient.dll over the bundled x64 one
   (the original is kept as nvdaControllerClient64.dll.x64.bak).
2. Patches accessible_output2/outputs/auto.py so outputs whose DLL cannot be
   loaded (PC-Talker, ZDSR, which have no ARM64 builds) are skipped instead of
   raising.

Run it with the same Python you use for QuickProof:

    python fix_arm64.py [NVDA_VERSION]

It is safe to run more than once. Re-run it after upgrading accessible_output2,
because pip will put the x64 DLL and the unpatched auto.py back.
"""

import io
import os
import platform
import shutil
import sys
import urllib.request
import zipfile

DEFAULT_NVDA_VERSION = "2026.1.1"
ZIP_URL = "https://www.nvaccess.org/files/nvda/releases/{v}/nvda_{v}_controllerClient.zip"
OLD_EXCEPT = "            except OutputError:\n"
NEW_EXCEPT = "            except (OutputError, OSError, AttributeError):\n"


def main():
    if platform.system() != "Windows" or platform.machine().upper() != "ARM64":
        print("This machine is not Windows on ARM; nothing to do.")
        return 0

    try:
        import accessible_output2
    except ImportError:
        print("accessible_output2 is not installed. Run: pip install -r requirements.txt")
        return 1

    pkg_dir = os.path.dirname(accessible_output2.__file__)
    lib_dir = os.path.join(pkg_dir, "lib")
    dll_path = os.path.join(lib_dir, "nvdaControllerClient64.dll")
    backup_path = dll_path + ".x64.bak"
    auto_path = os.path.join(pkg_dir, "outputs", "auto.py")

    version = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NVDA_VERSION
    url = ZIP_URL.format(v=version)
    print("Downloading", url)
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        arm64_dll = zf.read("arm64/nvdaControllerClient.dll")

    current = None
    if os.path.exists(dll_path):
        with open(dll_path, "rb") as f:
            current = f.read()
    if current == arm64_dll:
        print("ARM64 DLL already installed at", dll_path)
    else:
        if current is not None and not os.path.exists(backup_path):
            shutil.copy2(dll_path, backup_path)
            print("Backed up x64 DLL to", backup_path)
        try:
            with open(dll_path, "wb") as f:
                f.write(arm64_dll)
        except PermissionError:
            print("Cannot replace", dll_path)
            print("It is in use. End pythonw.exe in Task Manager (QuickProof) and run this script again.")
            return 1
        print("Installed ARM64 DLL to", dll_path)

    with open(auto_path, "r", encoding="utf-8", newline="") as f:
        src = f.read()
    if NEW_EXCEPT in src:
        print("auto.py already patched.")
    elif OLD_EXCEPT in src or OLD_EXCEPT.replace("\n", "\r\n") in src:
        src = src.replace(OLD_EXCEPT, NEW_EXCEPT).replace(
            OLD_EXCEPT.replace("\n", "\r\n"), NEW_EXCEPT.replace("\n", "\r\n")
        )
        with open(auto_path, "w", encoding="utf-8", newline="") as f:
            f.write(src)
        print("Patched", auto_path)
    else:
        print("Could not find the expected line in", auto_path, "- patch it by hand:")
        print("  change:", OLD_EXCEPT.strip())
        print("  to:    ", NEW_EXCEPT.strip())
        return 1

    # Sanity check: the speaker must now construct without raising.
    import importlib
    import accessible_output2.outputs.auto as auto
    importlib.reload(auto)
    speaker = auto.Auto()
    names = [type(o).__name__ for o in speaker.outputs]
    print("Speaker outputs available:", ", ".join(names))
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
