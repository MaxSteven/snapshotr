# -*- coding: utf-8 -*-
# --------------------------------------------------------------
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
# --------------------------------------------------------------
__version__ = "0.1.8"
__release__ = True

import nuke
import nukescripts
import os
import re
import time
import pwd
import threading
from PIL import Image
from PySide import QtCore
from sys import path

snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)
from . import markup, scandir

if nuke.GUI is True:
    class ssPanel(nukescripts.PythonPanel):

        def __init__(self):
            nukescripts.PythonPanel.__init__(
                self,
                'Snapshotr',
                'uk.co.thefoundry.ssPanel')

            global rootDir, snapsDir, DEV
            DEV = 0
            rootDir = str(nuke.script_directory())
            snapsDir = rootDir + "/snaps"

            if DEV > 0:
                print "\n* Debug mode ON"
                print "* rootDir inside ssPanel __init__ = " + rootDir
                print "* snapsDir inside ssPanel __init__ = " + snapsDir

            # Define knobs
            self.snapButton = nuke.PyScript_Knob('Full')
            self.instaButton = nuke.PyScript_Knob('Instant')
            self.ffButton = nuke.PyScript_Knob('Open')
            self.commentField = nuke.String_Knob('Comment:')
            self.divider = nuke.Text_Knob('')
            self.markNode = nuke.Boolean_Knob('Mark node ')
            self.timerValue = nuke.Int_Knob('Autosnap: ')

            # Add them to the panel
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

            re1='((?:[a-z][a-z]*[0-9]+[a-z0-9]*))'  # Shot
            re2='(\\.)'                             # .
            re3='((?:[a-z][a-z]+))'                 # Task
            re4='(\\.)'                             # .
            re5='((?:[a-z][a-z]+))'                 # Artist
            re6='(\\.)'                             # .
            re7='(v)'                               # v
            re8='(\\d+)'                            # Version number
            re9='(\\.)'                             # .
            re10='(nk)'                             # nk
            rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10,re.IGNORECASE|re.DOTALL)
            if rg.match(scriptName) is None:
                nuke.message("Please save your script in the following format:\nshot.task.artist.v00.nk")


            #
            # Create auto snapshot every 60 minutes
            #
            def snapAutosave():
                try:
                    scriptPath = nuke.toNode('root').knob('name').value()
                    scriptName = scriptPath.split("/")[-1]
                    timestamp = time.strftime("%d-%m-%Y") + '_' + time.strftime("%H-%M")
                    snapPath = snapsDir + '/' + scriptName + '_' + timestamp
                    snapScriptName = snapPath + "/" + scriptName + '_' + timestamp + '.nk'
                    snapImageFile = snapPath + "/" + scriptName + '_' + timestamp + '.jpg'
                    snapCommentFile = snapPath + "/" + scriptName + '_' + timestamp+ '.txt'
                    print "\n~ autosaving snapshot..."

                    #  Check if snapshots root exists and create _current_ autosnap directory
                    #
                    if rootDir != "" and snapsDir != "":
                        if not os.path.exists(snapsDir):
                            os.makedirs(snapsDir)
                            print "\n~ Created root snapshots dir: " + snapsDir
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
                    if DEV > 0:
                        print "\n~ ---- Calling from: " + str(threading.current_thread())
                        for x in threading.enumerate():
                            print "* " + str(x)

                    def captr():
                        if DEV > 0:
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
            snapPath = snapsDir + '/' + scriptName + '_' + timestamp
            snapScriptName = snapPath + "/" + \
                scriptName + '_' + timestamp + '.nk'
            snapImageFile = snapPath + "/" + \
                scriptName + '_' + timestamp + '.jpg'
            snapCommentFile = snapPath + "/" + \
                scriptName + '_' + timestamp + '.txt'
            currentFrame = int(nuke.frame())
            fakeFrameRange = str(currentFrame) + "-" + str(currentFrame)
            writeUniqueName = "tmp_Snapshotr" + timestamp
            if DEV > 0:
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
                if rootDir != "" and snapsDir != "":
                    if not os.path.exists(snapsDir):
                        os.makedirs(snapsDir)
                        print "\n~ Created root snapshots dir: " + snapsDir
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
            if DEV > 0:
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
            snapPath = snapsDir + '/' + scriptName + '_' + timestamp
            snapScriptName = snapPath + "/" + \
                scriptName + '_' + timestamp + '.nk'
            snapImageFile = snapPath + "/" + \
                scriptName + '_' + timestamp + '.jpg'
            snapCommentFile = snapPath + "/" + \
                scriptName + '_' + timestamp + '.txt'
            currentFrame = int(nuke.frame())
            fakeFrameRange = str(currentFrame) + "-" + str(currentFrame)
            writeUniqueName = "tmp_Snapshotr" + timestamp
            if DEV > 0:
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
                if rootDir != "" and snapsDir != "":
                    if not os.path.exists(snapsDir):
                        os.makedirs(snapsDir)
                        print "\n~ Created root snapshots dir: " + snapsDir
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
        def updateWebView(void):
            genStart = time.time()
            page = markup.page()

            title = "Snapshot viewer"
            scriptPath = str(os.path.dirname(os.path.abspath(__file__)))
            header = "<script src='" + scriptPath + "/bootstrap/js/jquery-2.1.1.min.js'></script>" \
                + "<script src='" + scriptPath + "/bootstrap/js/bootstrap.min.js'></script>" \
                + "<script src='" + scriptPath + "/bootstrap/js/bootstrap.lightbox.js'></script>" \
                + "<script src='" + scriptPath + "/bootstrap/js/jquery.tablesorter.min.js'></script>" \
                + "<br><br>&nbsp;<br />"
            css = (
                scriptPath +
                "/bootstrap/css/bootstrap.dark.min.css",
                scriptPath +
                "/bootstrap/css/bootstrap.lightbox.css",
                scriptPath +
                "/bootstrap/css/bootstrap.dark.addons.css")

            page.init(css=css, title=title, header=header)

            # Snaps root dir, list of snaps
            snapsIterator = scandir.walk(snapsDir)
            dirList = []
            for directory in snapsIterator:
                dirList.append(directory)

            if DEV > 1:
                print "\n ------------------------------ "
                for index, item in enumerate(dirList):
                    print "* dirList: " + str(index) + str(item)

            roots = dirList[0]
            if len(roots) < 1:
                print "\n! JohnnieWalker doesn't walk, here is what we've got: " + roots
                raise
            rootDir = str(roots[0])
            scriptPath = nuke.toNode('root').knob('name').value()
            scriptName = scriptPath.split("/")[-1]
            snapsList = roots[1:]

            if DEV > 1:
                print "\n ------------------------------ "
                print "* scriptName: " + scriptName
                print "* rootDir: " + rootDir

            if DEV > 1:
                print "\n ------------------------------ "
                print "* scriptName: " + scriptName
                print "* snapsList: " + str(snapsList)

            txtList = []
            userList = []

            # because os.stat() inside class crashes Nuke,
            # we are constructing bicycle here
            c = 0
            for ROOT, DIR, FILES in scandir.walk(snapsDir):
                for dir in DIR:
                    txtList.append(dir)
                for filex in FILES:
                    if filex.endswith('txt'):
                        txtList[c] = rootDir + "/" + \
                            str(txtList[c]) + "/" + filex
                        c += 1
                    else:
                        pass
            del c

            if DEV > 1:
                print "\n ------------------------------ "
                for index, item in enumerate(txtList):
                    print "* txtList: " + str(index) + " = " + str(item)

            for x in txtList:
                if os.path.exists(x) is True:
                    userOwner = pwd.getpwuid(os.stat(x).st_uid).pw_name
                    userList.append(userOwner)
                else:
                    pass

            if DEV > 1:
                print "\n ------------------------------ "
                for index, item in enumerate(userList):
                    print "* userList: " + str(index) + " = " + str(item)

            # Generate HTML
            # If anyone want to refactor this - you are welcome
            page.div(class_="navbar navbar-default navbar-fixed-top custom-nav")
            page.div(class_="container")
            page.div(class_="navbar-header")
            page.a("Snapshotr", href="#", class_="navbar-brand")
            page.div.close()
            page.div(class_="navbar-collapse collapse", id="navbar-main")
            page.ul(class_="nav navbar-nav")
            page.add('<li> \
                    <a href="#" data-toggle="modal" data-target="#helpModal">Help</a> \
                  </li>')
            page.add('<li> \
                    <a href="#" data-toggle="modal" data-target="#clogModal">Changelog</a> \
                  </li>')
            page.add("</ul></div></div></div>")
            page.div(class_="container")
            page.div(class_="row")
            page.div(class_="col-lg-12")
            page.h2(scriptName, id="type-blockquotes")
            page.div.close()
            page.div.close()
            page.div(class_="row")
            page.div(class_="col-lg-6")
            page.div(class_="bs-component")
            page.p(rootDir, class_="text-primary")  # root dir
            page.add("&nbsp;")
            page.div.close()
            page.div.close()
            page.div.close()

            # Proper output of the snaps
            page.div(class_="bs-component")
            page.table(
                class_="table table-condensed tablesorter",
                id="mainTableID")
            page.thead()
            page.tr()
            page.th("Snap image")
            page.th("Script link")
            page.th("User")
            page.th("Version")
            page.th("Time created")
            page.th("Comment")
            page.tr.close()
            page.thead.close()
            page.tbody()

            c = 0
            for snap in snapsList[0]:
                # Check for tags and output proper <tr> class
                cmntFilePath = str(roots[0]) + "/" + snap + "/" + snap + ".txt"
                if os.path.exists(cmntFilePath) is True:
                    pass
                else:
                    with open(cmntFilePath, "w+") as cmnt:
                        cmnt.write(" ")
                cmntFileObj = open(cmntFilePath)
                cmntList = cmntFileObj.read().split(" ")
                cmntTagChecker = [x for x in cmntList if "#" in x]
                # Tag detected, mark with corresponding color
                if len(cmntTagChecker) == 1:
                    if cmntTagChecker[0] == "#green":
                        page.tr(class_="success")
                    elif cmntTagChecker[0] == "#blue":
                        page.tr(class_="info")
                    elif cmntTagChecker[0] == "#red":
                        page.tr(class_="danger")
                    elif cmntTagChecker[0] == "#orange":
                        page.tr(class_="warning")
                    elif cmntTagChecker[0] == "#autosnap":
                        page.tr(class_="autosnap")
                    else:
                        page.tr(class_="active")
                # Multiple tags. Fuck it and mark as grey
                elif len(cmntTagChecker) > 1:
                    page.tr(class_="active")
                else:
                    page.tr()

                # Thumbnail
                imgPath = str(roots[0]) + "/" + snap + "/" + snap + ".jpg"
                imgThumbPath = str(
                    roots[0]) + "/" + snap + "/" + snap + ".thumb.jpg"
                page.add(
                    '<td class="vert-align thumbnails" data-toggle="lightbox"> <a href="' +
                    imgPath +
                    '" class="thumbnail">' +
                    ' <img src="' +
                    imgThumbPath +
                    '" height="100px" class="img-rounded" /></a></td>')

                # NK button
                tmpB = r'<td class="vert-align"><button type="button" class="btn btn-default has-popover" data-container="body" data-toggle="popover" data-placement="bottom" data-content="'
                btnCode = tmpB + \
                    str(roots[0]) + "/" + snap + "/" + snap + \
                    ".nk" + '">nk</button></td>'
                page.add(btnCode)

                # Username
                usrCode = '<td class="vert-align" style="color: #5c6266;">' + \
                    userList[c] + '</td>'
                c += 1
                page.add(usrCode)

                # Version
                version = snap.split(".")[-2]
                verCode = '<td class="vert-align" style="color: #5c6266;">' + \
                    version + '</td>'
                page.add(verCode)

                # Date-time combined
                dtSnap = snap.split("_")
                date = str(dtSnap[1]).split("-")
                dateTimeCode = ".".join(
                    date) + ' ' + str(dtSnap[2]).replace("-", ":")
                page.td(
                    dateTimeCode,
                    class_='vert-align',
                    style="color: #7A8288;")

                # Replace with tag-removed
                if len(cmntTagChecker) > 0:
                    for x in cmntTagChecker:
                        cmntList.remove(x)
                cmntOutText = ' '.join(cmntList)
                page.td(cmntOutText, class_="vert-align")
                page.tr.close()
            del c

            page.tbody.close()
            page.table.close()
            page.div.close()  # container

            page.add(' \n\
                <div class="modal fade" id="helpModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"> \n\
                  <div class="modal-dialog"> \n\
                    <div class="modal-content"> \n\
                      <div class="modal-header"> \n\
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button> \n\
                        <h4 class="modal-title" id="myModalLabel">Help</h4> \n\
                      </div> \n\
                      <div class="modal-body"> \n\
                        <p>This is <b>Snapshotr</b>, Nuke snapshot manager.<br />Pet project for November 2014, developed whenever I have free time and some coffee.</p> \n\
                        <p>If you have any questions, feel free to write me at <a href="mailto:art@artaman.net?Subject=Snapshotr" target="_top">art@artaman.net</a></p> \n\
                        <p></p> \n\
                      </div> \n\
                      <div class="modal-footer"> \n\
                        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button> \n\
                      </div> \n\
                    </div> \n\
                  </div> \n\
                </div>')

            page.add(' \n\
                <div class="modal fade" id="clogModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"> \n\
                  <div class="modal-dialog"> \n\
                    <div class="modal-content"> \n\
                      <div class="modal-header"> \n\
                        <button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button> \n\
                        <h4 class="modal-title" id="myModalLabel">Changelog</h4> \n\
                      </div> \n\
                      <div class="modal-body"> \n\
                        <p>v0.1.8 &mdash; first public release</p> \n\
                        <p>v0.1.6 &mdash; limited release for beta-testing</p> \n\
                      </div> \n\
                      <div class="modal-footer"> \n\
                        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button> \n\
                      </div> \n\
                    </div> \n\
                  </div> \n\
                </div>')

            page.add("<script type=\"text/javascript\"> \n\
                      $('body').popover({ \n\
                      selector: '.has-popover' \n\
          });</script>")

            page.add("<script> \n\
            $(document).ready(function(){ \n\
            $(function(){ \n\
            $('#mainTableID').tablesorter( \n\
            { \n\
            headers: { \n\
            0: { sorter: false }, \n\
            1: { sorter: false }, \n\
            2: { sorter: false }, \n\
            3: { sorter: false }, \n\
            4: { sorter: \"shortDate\", dateFormat: \"ddmmyyyy\", sortInitialOrder: 'desc'}, \n\
            5: { sorter: false }, \n\
            } \n\
            }); \n\
            $('#mainTableID').tablesorter(); \n\
            $('#mainTableID').trigger('update'); \n\
            var sorting = [[4,1]]; \n\
            $('#mainTableID').trigger('sorton',[sorting]); \n\
            }); \n\
            }); \n\
            </script>")

            genText = "<p class=\"text-primary\">Webpage generated in " + str(round(float(time.time() - genStart), 3)) + " sec. by " \
                      + str(os.getlogin()) + " at " + os.uname()[1] + "</p>"
            page.add(genText)
            page.p('&nbsp;')

            # Return page as tuple line-by-line
            page = str(page)
            pageList = page.split("\n")
            returnList = []
            for x in pageList:
                returnList.append(x + "\n")
            return returnList

        # What to do if specific knob changed
        #
        def knobChanged(self, knob):
            scriptPath = nuke.toNode('root').knob('name').value()
            scriptName = scriptPath.split("/")[-1]
            pFile = str(scriptName).split(".")
            pFile = "_".join(pFile[0:2])
            poFile = pFile
            pFile = snapsDir + "/" + pFile + ".html"
            if knob is self.snapButton:
                if self.ssSnap() > 0:
                    self.ssSnap()
                else:
                    try:
                        self.updateWebView()
                    except:
                        x = self.updateWebView()
                        print x
                        print "\n! self.updateWebView() call failed"
                    pageFile = open(pFile, "w+")
                    try:
                        pageFile.writelines(self.updateWebView())
                        pageFile.close()
                    except:
                        print "\n! pageFile.writelines(self.updateWebView()) writelines call failed\n"
            elif knob is self.ffButton:
                ffCommand = "firefox -new-tab " + pFile
                print "\n~ Opening " + poFile + ".html in a new tab"
                os.system(ffCommand)
            elif knob is self.instaButton:
                if self.instaSnap() > 0:
                    self.instaSnap()
                else:
                    try:
                        self.updateWebView()
                    except:
                        x = self.updateWebView()
                        print x
                        print "\n! self.updateWebView() call failed"
                    pageFile = open(pFile, "w+")
                    try:
                        pageFile.writelines(self.updateWebView())
                        pageFile.close()
                    except:
                        print "\n! pageFile.writelines(self.updateWebView()) writelines call failed\n"
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

    def addSSpanel():
        return ssPanel().addToPane()
else:
    pass

if nuke.GUI is True:
    menu = nuke.menu("Pane")
    menu.addCommand("Snapshotr", addSSpanel)
    nukescripts.registerPanel("uk.co.thefoundry.ssPanel", addSSpanel)
else:
    print "\n~ Nuke is running in non-gui mode, Snapshotr isn't activated"