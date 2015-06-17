from ConfigParser import SafeConfigParser
from sys import path
import os

snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)

settings = SafeConfigParser()
settings.read('settings.ini')

global VERSION, DEBUG, CONF_UPDATE, CONF_AUTOSNAP, CONF_ADD_HOTKEYS, HASHES, SS_PATH
VERSION = settings.get('common', 'version')
DEBUG = settings.get('common', 'debug')
CONF_UPDATE = settings.get('common', 'autoupdate')
CONF_AUTOSNAP = settings.get('common', 'snap_upon_load')
CONF_ADD_HOTKEYS = settings.get('common', 'add_hotkeys')
HASHES = {}
for module, sha in settings.items('hashes'):
    HASHES.update({module:sha})
SS_PATH = snapr_path