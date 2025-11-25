"""Constants for bfg-sync."""
from pathlib import Path
from appdirs import user_config_dir, user_data_dir

from psiutils.known_paths import resolve_path

LOCAL_SOURCE = Path(Path.home(), 'projects', 'bfg', 'bfg_api', 'src')
VERSION_URI = 'http://www.bidforgame.com/bfg/versions/'

REMOTE_BASE = 'bfg/bfg_wag'

# General
AUTHOR = 'Jeff Watkins'
APP_NAME = 'bfg-sync'
APP_AUTHOR = 'psionman'
HTML_DIR = resolve_path('html', __file__)
HELP_URI = ''

# Paths
CONFIG_PATH = Path(user_config_dir(APP_NAME, APP_AUTHOR), 'config.toml')
USER_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
HOME = str(Path.home())

DOWNLOAD_DIR = Path(Path.home(), 'ProjectData', 'bfg_sync')
REMOTE_DIR = 'bfg/bfg_wag'

# GUI
APP_TITLE = 'BfG Sync'
ICON_FILE = Path(Path(__file__).parent, 'images', 'icon.png')
DEFAULT_GEOMETRY = '400x500'

ALWAYS_IGNORE = [
    '__pycache__',
]
