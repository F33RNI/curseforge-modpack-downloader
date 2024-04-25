# -*- mode: python ; coding: utf-8 -*-

"""
Copyright (C) 2024 Fern Lane, curseforge-modpack-downloader

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
See the License for the specific language governing permissions and
limitations under the License.

IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import platform

import PyInstaller.config

# Set working path
PyInstaller.config.CONF["workpath"] = "./build"

# Parse version from _version.py file
with open("_version.py", "r", encoding="utf-8") as file:
    version = file.read().strip().split("__version__")[-1].split('"')[1]

SOURCE_FILES = ["main.py", "getch.py", "_version.py"]

COMPILE_NAME = f"curseforge-modpack-downloader-{platform.system()}-{platform.machine()}-{version}".lower()

# Files and folders to include inside builded binary
INCLUDE_FILES = [
    ("LICENSE", "."),
    ("README.md", "."),
]

block_cipher = None

a = Analysis(
    SOURCE_FILES,
    pathex=[],
    binaries=[],
    datas=INCLUDE_FILES,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["_bootlocale"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=COMPILE_NAME,
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
