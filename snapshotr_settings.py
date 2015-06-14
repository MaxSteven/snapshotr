from ConfigParser import SafeConfigParser
from sys import path
import os

snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)

def init():
    parser = SafeConfigParser()
    settings = parser.read('settings.ini')