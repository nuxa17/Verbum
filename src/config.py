"""Configuration module.

This module sets constants for paths depending
of the device the program is running, if it's frozen, etc.
"""

import os
import sys
import platform
import ctypes
import subprocess

OS_SYSTEM = platform.system()
OS_VERSION = platform.version()

FROZEN = getattr(sys, 'frozen', False)
#***********
#*  Paths  *
#***********

if FROZEN:
    # we are running in a bundle
    BUNDLE_DIR = sys._MEIPASS

    from pathlib import Path
    this_path = Path(os.path.dirname(sys.executable)).resolve()

    if str(this_path).endswith(".app/Contents/MacOS"):
        EXEC_PATH = os.path.expanduser('~/Library/Application Support/Verbum')
    else:
        EXEC_PATH = str(this_path.absolute())
else:
    # we are running in a normal Python environment
    BUNDLE_DIR = os.getcwd()
    EXEC_PATH = BUNDLE_DIR

DATA_DIR = os.path.join(BUNDLE_DIR, 'data')
CONFIG_DIR = os.path.join(BUNDLE_DIR, 'config')
RES_DIR = os.path.join(BUNDLE_DIR, 'res')

PATTERNS_FILE = os.path.join(CONFIG_DIR, 'default.json')
CONTRACTIONS_FILE = os.path.join(CONFIG_DIR, 'contractions.json')
TAGGER_FILE = 'taggers/maxent_treebank_pos_tagger/english.pickle'
SETTINGS_FILE = os.path.join(EXEC_PATH, 'verbum.ini')

ICON_FILE = os.path.join(RES_DIR, 'logo.ico')
MANUAL_FILE = os.path.join(RES_DIR, 'manual.pdf')

REPO_LINK = r"https://github.com/nuxa17/Verbum"

#*****************
#*  Launch file  *
#*****************

def launch_file(file: str):
    """Launch a file on it's predetermined program."""

    if OS_SYSTEM == "Windows":
        os.startfile(file)
    else:
        subprocess.call(["open", file])

# set nice dpi on Windows
# from https://gist.github.com/DarkMatterCore/cead1fcb2c2795fdccb35846453b4a2f
dpi_aware = False
win_vista = ((OS_SYSTEM == 'Windows') and (int(OS_VERSION[:OS_VERSION.find('.')]) >= 6))
if win_vista:
    dpi_aware = (ctypes.windll.user32.SetProcessDPIAware() == 1)
    if not dpi_aware:
        dpi_aware = (ctypes.windll.shcore.SetProcessDpiAwareness(2) == 0)
