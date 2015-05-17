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

__version__ = "0.2.0"
__release__ = True

import nuke
import nukescripts
import os
from sys import path

snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)

if nuke.GUI:
    def addSSpanel():
        import snapshotr_panel
        return snapshotr_panel.ssPanel().addToPane()
    menu = nuke.menu("Pane")
    menu.addCommand("Snapshotr", addSSpanel)
    nukescripts.registerPanel("uk.co.thefoundry.ssPanel", addSSpanel)