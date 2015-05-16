# -*- coding: utf-8 -*-
# --------------------! DEV BRANCH !----------------------------
# Snapshotr: Nuke snapshots manager
#
# Andrew Savchenko © 2014
# art@artaman.net
#
# Attribution 4.0 International (CC BY 4.0)
# http://creativecommons.org/licenses/by/4.0/
#
# Developed on OS X and RHEL, should work on random *nix system
#
# --------------------! DEV BRANCH !----------------------------

import nuke
import nukescripts
import os
import time
import threading
import webbrowser
from PIL import Image
# noinspection PyUnresolvedReferences
from PySide import QtCore
from sys import path
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)
import snapshotr_webView
import snapshotr_common as cmn

class ssPanel(nukescripts.PythonPanel):

    DEV = 1
    rootDir = nuke.script_directory()
    snapsDir = rootDir + "/snaps"


    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self,
            'Snapshotr',
            'uk.co.thefoundry.ssPanel')

        DEV = self.DEV
        rootDir = self.rootDir
        snapsDir = self.snapsDir

        if DEV > 0:
            print "\n* Debug mode ON"
            print "* rootDir inside ssPanel __init__ = " + rootDir
            print "* snapsDir inside ssPanel __init__ = " + snapsDir

        self.snapButton = nuke.PyScript_Knob('Full')
        self.instaButton = nuke.PyScript_Knob('Instant')
        self.ffButton = nuke.PyScript_Knob('Open')
        self.commentField = nuke.String_Knob('Comment:')
        self.divider = nuke.Text_Knob('')
        self.markNode = nuke.Boolean_Knob('Mark node ')
        self.timerValue = nuke.Int_Knob('Autosnap: ')

        self.addKnob(self.commentField)
        self.addKnob(self.instaButton)
        self.addKnob(self.snapButton)
        self.addKnob(self.ffButton)
        self.addKnob(self.timerValue)
        self.addKnob(self.divider)
        self.addKnob(self.markNode)
        self.timerValue.setValue(60) # 60 minutes by default

        scriptPath = nuke.toNode('root').knob('name').value()
        scriptName = scriptPath.split("/")[-1]

        if cmn.check_script(name=scriptName) is None:
            nuke.message("Please save your script in the following format:\nshot.task.artist.v00.00.nk")
            raise BaseException


        def snapAutosave():
            """
            Create auto snapshot, start timer to trigger this (every 60min by default)
            """
            try:
                c_var = cmn.init_common_vars(snapsDir=self.snapsDir)
                print "\n~ autosaving snapshot..."
                cmn.create_snapshot_dirs(rootDir=self.rootDir, snapsDir=self.snapsDir,
                                         snapPath=c_var["snapPath"], markNode=self.markNode)
                cmn.create_snapshot_script(scriptPath=c_var["scriptPath"], snapScriptName=c_var["snapScriptName"])
                cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"])
                cmn.create_snapshot_screenshot(DEV=self.DEV, snapImageFile=c_var["snapImageFile"])
            finally:
                timer = int(self.timerValue.value()) * 60000
                QtCore.QTimer.singleShot(timer, snapAutosave)

        snapAutosave()


    def instaSnap(self):
        """
        Create instant snapshot of current active viewer
        """
        c_var = cmn.init_common_vars(snapsDir=self.snapsDir)
        cmn.create_snapshot_dirs(rootDir=self.rootDir, snapsDir=self.snapsDir,
                                 snapPath=c_var["snapPath"],markNode=self.markNode)
        cmn.create_snapshot_script(scriptPath=c_var["scriptPath"], snapScriptName=c_var["snapScriptName"])
        cmn.label_node(markNode=self.markNode, nodeLabel=c_var["nodeLabel"])
        cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"])
        cmn.create_snapshot_screenshot(DEV=self.DEV, snapImageFile=c_var["snapImageFile"])


    def ssSnap(self):
        """
        Create full-res snapshot via BG render
        """
        c_var = cmn.init_common_vars(snapsDir=self.snapsDir)
        cmn.create_snapshot_dirs(rootDir=self.rootDir, snapsDir=self.snapsDir,
                                 snapPath=c_var["snapPath"],markNode=self.markNode)
        cmn.create_snapshot_script(scriptPath=c_var["scriptPath"], snapScriptName=c_var["snapScriptName"])
        cmn.label_node(markNode=self.markNode, nodeLabel=c_var["nodeLabel"])
        cmn.create_snapshot_fullres(snapImageFile=c_var["snapImageFile"], writeUniqueName=c_var["writeUniqueName"],
                                    fakeFrameRange=c_var["fakeFrameRange"])
        cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"])
    #
    # Create web view
    #
    updateWebView = snapshotr_webView.updateWebView(debug=DEV, s_dirs=snapsDir)

    #
    # What to do if specific knob changed
    #
    def knobChanged(self, knob):

        updateWebView = snapshotr_webView.updateWebView(debug=self.DEV, s_dirs=self.snapsDir)

        scriptPath = nuke.toNode('root').knob('name').value()
        scriptName = scriptPath.split("/")[-1]
        pFile = str(scriptName).split(".")
        pFile = "_".join(pFile[0:2])
        poFile = pFile
        pFile = self.snapsDir + "/" + pFile + ".html"
        if knob is self.snapButton:
            if self.ssSnap() > 0:
                self.ssSnap()
            else:
                try:
                    updateWebView()
                except:
                    x = updateWebView()
                    print x
                    print "\n! self.updateWebView() call failed"
                pageFile = open(pFile, "w+")
                try:
                    pageFile.writelines(updateWebView())
                    pageFile.close()
                except:
                    print "\n! pageFile.writelines(updateWebView()) writelines call failed\n"
        elif knob is self.ffButton:
            webbrowser.open('file://' + os.path.realpath(pFile), new=2, autoraise=True)
            print "\n~ Opening " + poFile + ".html in a new tab..."
        elif knob is self.instaButton:
            self.instaSnap()
            try:
                updateWebView()
            except:
                x = updateWebView()
                print x
                print "\n! updateWebView() call failed"
            pageFile = open(pFile, "w+")
            try:
                pageFile.writelines(updateWebView())
                pageFile.close()
            except:
                print "\n! pageFile.writelines(updateWebView()) writelines call failed\n"
        elif knob is self.timerValue:
            if self.timerValue.value() < 10:
                self.timerValue.setValue(10)
            elif self.timerValue.value() > 60:
                self.timerValue.setValue(60)
            else:
                pass
        elif knob is self.markNode or self.commentField:
            pass
        else:
            self.notCatched()

    def notCatched(self):
        print "\n! Unknown knob changed"