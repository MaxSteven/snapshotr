# -*- coding: utf-8 -*-
# ------------------------------------------------
# Snapshotr: Nuke snapshots manager
#
# Andrew Savchenko © 2014-2015
# art@artaman.net
#
# Attribution 4.0 International (CC BY 4.0)
# http://creativecommons.org/licenses/by/4.0/
#
# Developed on OS X and RHEL, should work on random *nix system
#
# ------------------------------------------------

import nuke
import hashlib
import os
import time
import json
from sys import argv
from urllib import urlopen, urlretrieve
from distutils.version import StrictVersion
from sys import path
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)

__version__ = "0.1.0"

json_parsed = {}

def update_message():
    #TODO: Add message "What's updated in the new version"
    if nuke.ask('New version of "Snapshotr" found.\nWould you like to update?'):
        return True

class CheckHashes():
    def __init__(self):
        self.hashes_path = os.path.dirname(os.path.realpath(argv[0])) + "/snapshotr_hashes.json"

    def read_hashes(self):
        if os.access(self.hashes_path, os.R_OK):
            with open(self.hashes_path) as fp:
                return fp.read()
        return None

    def validate_hashes(self, ss_path=None):
        hashes_json = self.read_hashes()
        hashes_parsed = json.loads(hashes_json)
        if isinstance(hashes_parsed, dict):
            for module in hashes_parsed.iteritems():
                module_path = ss_path + "/" + module
                if os.path.isfile(module_path):
                    if hashes_parsed[module] == hashlib.sha256(open(module_path, 'rb').read()).hexdigest():
                        #TODO: Pass to logging in the future
                        print "* %s is OK" %module
                    print "! %s is modified" %module
                print "%s not found (but expected to be)" %module


def backup_current_version():
    """
    :return: True if everything went fine
    """
    timestamp = time.strftime("%d-%m-%Y") + '_' + time.strftime("%H-%M")
    backup_folder = os.path.expanduser("~/.nuke/snapshotr_backup")
    backup_command = "zip -r " + backup_folder + "/backup_" + timestamp + ".zip "\
                     + os.path.expanduser("~/.nuke/snapshotr/")
    if not os.path.exists(backup_folder):
        try:
            os.makedirs(backup_folder)
        except OSError, e:
            nuke.message("Can't create folder: %s" %e)
    if os.system(backup_command) == 0:
        return True


def generate_response(source=None):
    if source == "https":
        return urlopen("https://raw.githubusercontent.com/artaman/snapshotr/master/__init__.py")
    if source == "json":
        return urlopen("https://api.github.com/repos/artaman/snapshotr/releases/latest")


def get_json(out=json_parsed):
    #TODO: Add JSON validation
    response = generate_response(source="json")
    json_data = json.loads(response.read())
    if json_data:
        remote_version_json = str(json_data["name"]).translate(None, "v")
        download_link = str(json_data["zipball_url"])
        out.update({"version":remote_version_json, "download_link":download_link})
        return out


def check_new_version():
    """
    :return: True if everything OK
    """
    response = generate_response(source="https")
    remote_version = ""
    for ln in response:
        if "__version__" in ln:
            remote_version = ln.rstrip()
    remote_version_https = remote_version.split("=")[1].translate(None, '"').lstrip()

    get_json()

    if json_parsed:
        if StrictVersion(remote_version_https) == StrictVersion(json_parsed["version"]):
            print "Master branch and release are synced, processing..."
            if StrictVersion(json_parsed["version"]) > StrictVersion(__version__):
                return True


def download_new_version():
    link = json_parsed["download_link"]
    new_version_folder = "/".join(os.path.expanduser(snapr_path).split("/")[:-1]) + \
                       "/snapshotr_versions"
    new_version_path = new_version_folder + "/snapshotr_v" + json_parsed["version"] + ".zip"
    if not os.path.exists(new_version_folder):
        try:
            os.makedirs(new_version_folder)
        except OSError, e:
            nuke.message("Can't create folder: %s" %e)
    try:
        urlretrieve(url=link, filename=new_version_path)
        return True
    except OSError, e:
        nuke.message("Can't save the file: %s" %e)

def git_new_version():
    git_command = "cd %s && git pull https://github.com/artaman/snapshotr.git ." %snapr_path
    if os.system(git_command) == 0:
        return True
