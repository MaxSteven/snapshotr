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
import nukescripts
from sys import path
from .snapshotr_settings import *
path.append(SS_PATH)

if nuke.GUI:
    def addSSpanel():
        import snapshotr_panel
        return snapshotr_panel.ssPanel().addToPane()
    menu = nuke.menu("Pane")
    menu.addCommand("Snapshotr", addSSpanel)
    nukescripts.registerPanel("uk.co.thefoundry.ssPanel", addSSpanel)