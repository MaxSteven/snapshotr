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
from urllib import urlopen, urlretrieve
import json
from distutils.version import StrictVersion
from sys import path
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)

__version__ = "0.1.0" # TODO: Finally move this in one place and stop defining in every module

def update_message():
    if nuke.ask('New version of "Snapshotr" found.\nWould you like to update?'):
        return True


def check_modules_exist():
    found_modules = []
    for filex in os.listdir(snapr_path):
        if filex in known_modules:
            found_modules.append(filex)
    if len(known_modules) == len(found_modules):
        print "\n~ Starting update, found " + str(len(found_modules)) + " known modules"
        return True


class CheckHashes():
    def __init__(self):
        self.hashes_path = os.path.dirname(os.path.realpath(sys.argv[0])) + "/snapshotr_hashes.json"

    def read_hashes(self):
        if os.access(self.hashes_path, os.R_OK):
            with open(self.hashes_path) as fp:
                return fp.read()
        return None

    def validate_hashes(self, ss_path=None):
        hashes_json = self.read_hashes()
        hashes_parsed = json.loads(hashes_json)
        if isinstance(hashes_parsed, dict):
            for module, hash in hashes_parsed.iteritems():
                module_path = ss_path + "/" + module
                if hashes_parsed[module] == hashlib.sha256(open(module_path, 'rb').read()).hexdigest():
                    # Should pass to logging in the future
                    print "* " + module + " is OK"
                else:
                    print "! " + module + " is modified"


def backup_current_version():
    """
    :return: True if everything went fine
    """
    timestamp = time.strftime("%d-%m-%Y") + '_' + time.strftime("%H-%M")
    backup_folder = os.path.expanduser("~/.nuke/snapshotr_backup")
    backup_command = "zip -r " + backup_folder + "/backup_" + timestamp + ".zip "\
                     + os.path.expanduser("~/.nuke/snapshotr/")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    if os.system(backup_command) == 0:
        return True


def generate_response(what=None):
    if what == "https":
        return urlopen("https://raw.githubusercontent.com/artaman/snapshotr/master/__init__.py")
    if what == "json":
        return urlopen("https://api.github.com/repos/artaman/snapshotr/releases/latest")


json_parsed = {}

def get_json(out=json_parsed):
    response = generate_response(what="json")
    json_data = json.loads(response.read())
    remote_version_json = str(json_data["name"]).translate(None, "v")
    download_link = str(json_data["zipball_url"])
    out.update({"version":remote_version_json, "download_link":download_link})
    return out


def check_new_version():
    """
    :return: TBD
    """
    response = generate_response(what="https")
    remote_version = ""
    for ln in response:
        if "__version__" in ln:
            remote_version = ln.rstrip()
    remote_version_https = remote_version.split("=")[1].translate(None, '"').lstrip()

    get_json()

    if StrictVersion(remote_version_https) == StrictVersion(json_parsed["version"]):
        print "Master branch and release are the same version"
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

def extract_new_version():
    pass