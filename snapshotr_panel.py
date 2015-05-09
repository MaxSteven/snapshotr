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

    DEV = 2
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

        if cmn.check_script(scriptName) is None:
            nuke.message("Please save your script in the following format:\nshot.task.artist.v00.00.nk")


        #
        # Create auto snapshot every 60 minutes by default
        #
        def snapAutosave():
            try:
                scriptPath = nuke.toNode('root').knob('name').value()
                scriptName = scriptPath.split("/")[-1]
                timestamp = time.strftime("%d-%m-%Y") + '_' + time.strftime("%H-%M")
                snapPath = self.snapsDir + '/' + scriptName + '_' + timestamp
                snapScriptName = snapPath + "/" + scriptName + '_' + timestamp + '.nk'
                snapImageFile = snapPath + "/" + scriptName + '_' + timestamp + '.jpg'
                snapCommentFile = snapPath + "/" + scriptName + '_' + timestamp+ '.txt'
                print "\n~ autosaving snapshot..."

                #  Check if snapshots root exists and create _current_ autosnap directory
                #
                if self.rootDir != "" and self.snapsDir != "":
                    if not os.path.exists(self.snapsDir):
                        os.makedirs(self.snapsDir)
                        print "\n~ Created root snapshots dir: " + self.snapsDir
                else:
                    nuke.message("Please save your script")
                    return 0
                if not os.path.exists(snapPath):
                    os.makedirs(snapPath)
                    print "\n ------------ Autosnap @ " + time.strftime("%H:%M") + " ------------"
                    print "\n~ Created autosnap dir: " + snapPath
                else:
                    print "\n! Autosnap failed, directory exists"
                    return 0

                # Write script with a proper naming
                #
                try:
                    tmpScriptPath = scriptPath
                    print "\n~ Writing script (auto): " + str(snapScriptName)
                    nuke.scriptSaveAs(str(snapScriptName))
                    os.chmod(snapScriptName, 0444)
                    rootNode = nuke.toNode('root')
                    rootNode.knob('name').setValue(tmpScriptPath)
                    del tmpScriptPath
                except:
                    nuke.message("\n! Can't save the script, no autosnap created")
                    return 0

                # Write comment
                #
                try:
                    snapCommentFileObj = open(snapCommentFile, "w+")
                    commentText = "#autosnap"
                    snapCommentFileObj.write(commentText)
                    snapCommentFileObj.close()
                    os.chmod(snapCommentFile, 0444)
                    print "\n~ Writing text comment (auto): " + snapCommentFile
                except:
                    print "\n! Writing comment failed"
                    return 0

                # Write autosnap image
                #
                print "\n~ Writing autosnap screenshot: " + str(snapImageFile)
                if self.DEV > 0:
                    print "\n~ ---- Calling from: " + str(threading.current_thread())
                    for x in threading.enumerate():
                        print "* " + str(x)

                def captr():
                    if self.DEV > 0:
                        print "* executeInMainThread(): " + str(threading.current_thread())
                    nuke.activeViewer().node().capture(snapImageFile)
                nuke.executeInMainThread(captr)
                im = Image.open(snapImageFile)
                imSize = ('', 100)
                im.thumbnail(imSize, Image.ANTIALIAS)
                imgPathThumb = str(snapImageFile).replace('jpg', 'thumb') + '.jpg'
                im.save(imgPathThumb, 'JPEG')
                os.chmod(snapImageFile, 0444)
                os.chmod(imgPathThumb, 0444)
            finally:
                timer = int(self.timerValue.value()) * 60000
                QtCore.QTimer.singleShot(timer, snapAutosave)

        snapAutosave()


    #
    # Create instant snapshot of current active viewer
    #
    def instaSnap(self):
        scriptPath = nuke.toNode('root').knob('name').value()
        scriptName = scriptPath.split("/")[-1]
        timestamp = time.strftime(
            "%d-%m-%Y") + '_' + time.strftime("%H-%M")
        nodeLabel = "<b>SNAP</b><br />" + str(time.strftime("%d-%m-%Y")).replace(
            "-", ".") + ' ' + str(time.strftime("%H-%M")).replace("-", ":")
        snapPath = self.snapsDir + '/' + scriptName + '_' + timestamp
        snapScriptName = snapPath + "/" + \
                         scriptName + '_' + timestamp + '.nk'
        snapImageFile = snapPath + "/" + \
                        scriptName + '_' + timestamp + '.jpg'
        snapCommentFile = snapPath + "/" + \
                          scriptName + '_' + timestamp + '.txt'
        currentFrame = int(nuke.frame())
        fakeFrameRange = str(currentFrame) + "-" + str(currentFrame)
        writeUniqueName = "tmp_Snapshotr" + timestamp
        if self.DEV > 0:
            print "\n* scriptPath in ssSnap(): " + scriptPath
            print "* scriptName in ssSnap(): " + scriptName
            print "* timestamp in ssSnap(): " + timestamp
            print "* nodeLabel in ssSnap(): " + nodeLabel
            print "* snapPath in ssSnap(): " + snapPath
            print "* snapScriptName in ssSnap(): " + snapScriptName
            print "* snapImageFile in ssSnap(): " + snapImageFile
            print "* snapCommentFile in ssSnap(): " + snapCommentFile
            print "* currentFrame in ssSnap(): " + str(currentFrame)
            print "* fakeFrameRange in ssSnap(): " + str(fakeFrameRange)
            print "* writeUniqueName in ssSnap(): " + str(writeUniqueName) + "\n"

        # Check if snapshots root exists and create _current_ snapshot directory
        #
        try:
            if self.markNode.value() is True:
                nuke.selectedNode()
                if len(nuke.selectedNodes("Viewer")) > 0:
                    nuke.message("Can't run from viewer, select regular node")
                    return 0
            if self.rootDir != "" and self.snapsDir != "":
                if not os.path.exists(self.snapsDir):
                    os.makedirs(self.snapsDir)
                    print "\n~ Created root snapshots dir: " + self.snapsDir
            else:
                nuke.message("Save your script first")
                return 0
            if not os.path.exists(snapPath):
                os.makedirs(snapPath)
                print "\n ------------ Snap @ " + time.strftime("%H:%M") + " ------------"
                print "\n~ Created current snapshot dir: " + snapPath
            else:
                nuke.message(
                    "One snapshot per minute, per customer. Restrictions apply.")
                return 0
        except ValueError:
            nuke.message("'Mark node' is checked, but no node selected")
            return 0

        # Write script with a proper naming
        #
        try:
            tmpScriptPath = scriptPath
            print "\n~ Writing script: " + str(snapScriptName)
            nuke.scriptSaveAs(str(snapScriptName))
            os.chmod(snapScriptName, 0444)
            rootNode = nuke.toNode('root')
            rootNode.knob('name').setValue(tmpScriptPath)
        except:
            nuke.message("\n! Can't save the script, no snapshot created")
            return 0

        # Label node from which snap is rendered
        #
        if self.markNode.value() is True:
            try:
                nuke.selectedNode()
                if self.markNode.value() is True:
                    nuke.selectedNode().knob('tile_color').setValue(112233)
                    nuke.selectedNode().knob('label').setValue(nodeLabel)
                else:
                    pass
            except:
                print "\n! Labeling node failed"
                return 0

        # Write comment
        #
        try:
            snapCommentFileObj = open(snapCommentFile, "w+")
            commentText = self.commentField.getText()
            snapCommentFileObj.write(commentText)
            snapCommentFileObj.close()
            os.chmod(snapCommentFile, 0444)
            self.commentField.setText("")
            print "\n~ Writing text comment: " + snapCommentFile + "\n"
        except:
            print "\n! Writing comment failed"
            return 0

        # Write image in main thread
        #
        if self.DEV > 0:
            v = "viView = nuke.activeViewer()"
            o = "viObj = viView.node()"
            c = "viObj.capture(" + str(snapImageFile) + ")"
            print "\n ~~~~~~~~~~~~~ \n" + v + "\n" + o + "\n" + c + "\n ~~~~~~~~~~~~~ \n"
        try:
            viView = nuke.activeViewer()
            viObj = viView.node()
            viObj.capture(snapImageFile)
            im = Image.open(snapImageFile)
            imSize = ('', 100)
            im.thumbnail(imSize, Image.ANTIALIAS)
            imgPathThumb = str(snapImageFile).replace(
                'jpg',
                'thumb') + '.jpg'
            im.save(imgPathThumb, 'JPEG')
            os.chmod(snapImageFile, 0444)
            os.chmod(imgPathThumb, 0444)
        except:
            print "\n! Writing instant snapshot failed"
            return 0


    #
    # Create snapshot with BG render
    #
    def ssSnap(self):
        scriptPath = nuke.toNode('root').knob('name').value()
        scriptName = scriptPath.split("/")[-1]
        timestamp = time.strftime(
            "%d-%m-%Y") + '_' + time.strftime("%H-%M")
        nodeLabel = "<b>SNAP</b><br />" + str(time.strftime("%d-%m-%Y")).replace(
            "-", ".") + ' ' + str(time.strftime("%H-%M")).replace("-", ":")
        snapPath = self.snapsDir + '/' + scriptName + '_' + timestamp
        snapScriptName = snapPath + "/" + \
                         scriptName + '_' + timestamp + '.nk'
        snapImageFile = snapPath + "/" + \
                        scriptName + '_' + timestamp + '.jpg'
        snapCommentFile = snapPath + "/" + \
                          scriptName + '_' + timestamp + '.txt'
        currentFrame = int(nuke.frame())
        fakeFrameRange = str(currentFrame) + "-" + str(currentFrame)
        writeUniqueName = "tmp_Snapshotr" + timestamp
        if self.DEV > 0:
            print "\n* scriptPath in ssSnap(): " + scriptPath
            print "* scriptName in ssSnap(): " + scriptName
            print "* timestamp in ssSnap(): " + timestamp
            print "* nodeLabel in ssSnap(): " + nodeLabel
            print "* snapPath in ssSnap(): " + snapPath
            print "* snapScriptName in ssSnap(): " + snapScriptName
            print "* snapImageFile in ssSnap(): " + snapImageFile
            print "* snapCommentFile in ssSnap(): " + snapCommentFile
            print "* currentFrame in ssSnap(): " + str(currentFrame)
            print "* fakeFrameRange in ssSnap(): " + str(fakeFrameRange)
            print "* writeUniqueName in ssSnap(): " + str(writeUniqueName) + "\n"

        # Check if snapshots root exists and create _current_ snapshot directory
        #
        try:
            nuke.selectedNode()
            if len(nuke.selectedNodes("Viewer")) > 0:
                nuke.message("Can't run from viewer, select regular node")
                return 0
            if self.rootDir != "" and self.snapsDir != "":
                if not os.path.exists(self.snapsDir):
                    os.makedirs(self.snapsDir)
                    print "\n~ Created root snapshots dir: " + self.snapsDir
            else:
                nuke.message("Save your script first")
                return 0
            if not os.path.exists(snapPath):
                os.makedirs(snapPath)
                print "\n ------------ Snap @ " + time.strftime("%H:%M") + " ------------"
                print "\n~ Created current snapshot dir: " + snapPath
            else:
                nuke.message(
                    "One snapshot per minute, per customer. Restrictions apply.")
                return 0
        except ValueError:
            nuke.message("Select node first")
            return 0

        # Write script with a proper naming
        #
        try:
            tmpScriptPath = scriptPath
            print "\n~ Writing script: " + str(snapScriptName)
            nuke.scriptSaveAs(str(snapScriptName))
            os.chmod(snapScriptName, 0444)
            rootNode = nuke.toNode('root')
            rootNode.knob('name').setValue(tmpScriptPath)
        except:
            nuke.message("\n! Can't save the script, no snapshot created")
            return 0

        # Copy VIEWER_INPUT process
        #
        def copyViewerInput(node):
            orig = nuke.selectedNodes()
            [x.setSelected(False) for x in nuke.selectedNodes()]
            node.setSelected(True)
            nuke.nodeCopy("%clipboard%")
            node.setSelected(False)
            nuke.nodePaste("%clipboard%")
            new_node = nuke.selectedNode()
            [x.setSelected(False) for x in nuke.selectedNodes()]
            [x.setSelected(True) for x in orig]
            return new_node

        # Label node from which snap is rendered
        #
        try:
            nuke.selectedNode()
            if self.markNode.value() is True:
                nuke.selectedNode().knob('tile_color').setValue(112233)
                nuke.selectedNode().knob('label').setValue(nodeLabel)
            else:
                pass

            # Check if input process and viewer input are valid,
            # bake LUT, write full-res image, thumbnail, chmod 0444 both
            #
            orig = nuke.selectedNodes()[0]
            ip_node = nuke.activeViewer().node().knob('input_process_node').value()
            viewerInput = nuke.toNode(ip_node)
            viewerProcess = nuke.ViewerProcess.node()
            is_ip_valid = False
            is_vp_valid = False
            if 'None' not in str(viewerProcess):
                is_vp_valid = True
                root = nuke.root()
                root.begin()
                newVp = nuke.createNode(viewerProcess.Class(), viewerProcess.writeKnobs(nuke.WRITE_NON_DEFAULT_ONLY | nuke.TO_SCRIPT), inpanel=False)
                root.end()
                tmpViewerProcess = nuke.toNode(newVp.name())
                tmpViewerProcess.setInput(0, nuke.selectedNode())
                orig.setSelected(False)
                tmpViewerProcess.setSelected(True)
                orig = nuke.selectedNodes()[0]
            else:
                print "\n! No valid IP attached to the Viewer, going on..."
            if 'Node' in str(type(viewerInput)) or 'Gizmo' in str(type(viewerInput)):
                is_ip_valid = True
                newIp = copyViewerInput(viewerInput)
                tmpViewerInput = nuke.toNode(newIp.name())
                tmpViewerInput.setInput(0, nuke.selectedNode())
                orig.setSelected(False)
                tmpViewerInput.setSelected(True)
            else:
                print "\n! No valid VI attached to the Viewer, going on..."

            nuke.nodes.Colorspace(
                name="cspTmp89",
                colorspace_in="sRGB").setInput(0, nuke.selectedNode())
            csp = nuke.toNode('cspTmp89') # This name is cool enough to be hard-coded
            csp.setSelected(True)
            if is_ip_valid:
                tmpViewerInput.setSelected(False)
            if is_vp_valid:
                tmpViewerProcess.setSelected(False)

            finWriteTxt = "finWrite = " + '"' + \
                          r"import os\nfrom PIL import Image\nimgPath = nuke.thisNode()['file'].getValue()\nim = Image.open(imgPath)\nimSize = ('', 100)\nim.thumbnail(imSize, Image.ANTIALIAS)\nimgPathThumb = str(imgPath).replace('jpg', 'thumb') + '.jpg'\nim.save(imgPathThumb, 'JPEG')\nos.chmod(imgPath, 0444)\nos.chmod(imgPathThumb, 0444)" + \
                          '"' + r"; exec finWrite"
            print "\n~ Writing screenshot: " + snapImageFile
            nuke.nodes.Write(name=writeUniqueName,
                             file=snapImageFile,
                             colorspace="sRGB",
                             file_type="jpeg").setInput(0, nuke.selectedNode())
            writeUniqueNode = nuke.toNode(writeUniqueName)
            writeUniqueNode.knob('afterRender').setValue(finWriteTxt)
            nuke.executeBackgroundNuke(
                nuke.EXE_PATH,
                [writeUniqueNode],
                nuke.FrameRanges(fakeFrameRange),
                ["main"],
                {})
            nuke.delete(writeUniqueNode)
            nuke.delete(csp)
            if is_ip_valid:
                nuke.delete(tmpViewerInput)
            if is_vp_valid:
                nuke.delete(tmpViewerProcess)
        except ValueError:
            nuke.message("Select node first")
            return 0

        # Write comment
        #
        try:
            snapCommentFileObj = open(snapCommentFile, "w+")
            commentText = self.commentField.getText()
            snapCommentFileObj.write(commentText)
            snapCommentFileObj.close()
            os.chmod(snapCommentFile, 0444)
            self.commentField.setText("")
            print "\n~ Writing text comment: " + snapCommentFile + "\n"
        except:
            print "\n! Writing comment failed"
            return 0


    #
    # Create web view
    #
    # updateWebView = snapshotr_webView.updateWebView(debug=DEV, s_dirs=snapsDir)

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