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
import webbrowser
# noinspection PyUnresolvedReferences
from PySide import QtCore
from sys import path
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)
import snapshotr_webView
import snapshotr_common as cmn

class ssPanel(nukescripts.PythonPanel):

    DEV = 2
    rootDir = nuke.script_directory()
    snapsDir = rootDir + "/snaps"


    def __init__(self):
        nukescripts.PythonPanel.__init__(
            self,
            'Snapshotr',
            'uk.co.thefoundry.ssPanel')

        if self.DEV > 0:
            print "\n* Debug mode ON"
            print "* rootDir inside ssPanel __init__ = " + self.rootDir
            print "* snapsDir inside ssPanel __init__ = " + self.snapsDir

        self.btn_snap_fullres = nuke.PyScript_Knob('Full')
        self.btn_snap_instant = nuke.PyScript_Knob('Instant')
        self.btn_open_webview = nuke.PyScript_Knob('Open')
        self.commentField = nuke.String_Knob('Comment:')
        self.divider = nuke.Text_Knob('')
        self.markNode = nuke.Boolean_Knob('Mark node ')
        self.timerValue = nuke.Int_Knob('Autosnap: ')

        self.addKnob(self.commentField)
        self.addKnob(self.btn_snap_instant)
        self.addKnob(self.btn_snap_fullres)
        self.addKnob(self.btn_open_webview)
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
                cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"], commentText="#autosnap")
                cmn.create_snapshot_screenshot(DEV=self.DEV, snapImageFile=c_var["snapImageFile"])
            finally:
                timer = int(self.timerValue.value()) * 60000
                QtCore.QTimer.singleShot(timer, snapAutosave)

        snapAutosave()


    def snap_instant(self):
        """
        Create instant snapshot of current active viewer
        """
        c_var = cmn.init_common_vars(snapsDir=self.snapsDir)
        cmn.create_snapshot_dirs(rootDir=self.rootDir, snapsDir=self.snapsDir,
                                 snapPath=c_var["snapPath"],markNode=self.markNode)
        cmn.create_snapshot_script(scriptPath=c_var["scriptPath"], snapScriptName=c_var["snapScriptName"])
        cmn.label_node(markNode=self.markNode, nodeLabel=c_var["nodeLabel"])
        cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"], commentText=self.commentField.getText())
        cmn.create_snapshot_screenshot(DEV=self.DEV, snapImageFile=c_var["snapImageFile"])


    def snap_fullres(self): # TODO: Add detection if running from viewer
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
        cmn.create_snapshot_comment(snapCommentFile=c_var["snapCommentFile"], commentText=self.commentField.getText())


    def knobChanged(self, knob):
        """
        :param knob: certain knob within panel
        """
        scriptPath = nuke.toNode('root').knob('name').value()
        scriptName = scriptPath.split("/")[-1]
        pFile = str(scriptName).split(".")
        pFile = "_".join(pFile[0:2])
        pFile = self.snapsDir + "/" + pFile + ".html"

        if knob is self.btn_snap_fullres:
            self.snap_fullres()
            webview_html = snapshotr_webView.updateWebView(debug=self.DEV, s_dirs=self.snapsDir)
            cmn.write_html(pFile=pFile, html=webview_html)
        elif knob is self.btn_snap_instant:
            self.snap_instant()
            webview_html = snapshotr_webView.updateWebView(debug=self.DEV, s_dirs=self.snapsDir)
            cmn.write_html(pFile=pFile, html=webview_html)
        elif knob is self.btn_open_webview:
            webbrowser.open('file://' + os.path.realpath(pFile), new=2, autoraise=True)
        elif knob is self.timerValue:
            if self.timerValue.value() < 10:
                self.timerValue.setValue(10)
            elif self.timerValue.value() > 60:
                self.timerValue.setValue(60)
        else:
            pass