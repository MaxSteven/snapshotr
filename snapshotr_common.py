# -*- coding: utf-8 -*-
# ------------------------------------------------
# Snapshotr: Nuke snapshots manager
#
# Andrew Savchenko © 2014-2015
# andrew@savchenko.net
#
# Attribution 4.0 International (CC BY 4.0)
# http://creativecommons.org/licenses/by/4.0/
#
# Developed on OS X and RHEL, should work on random *nix system
#
# ------------------------------------------------

__version__ = "0.2.0"
__release__ = True

import re
import nuke
import time
import os
try:
    from PIL import Image
except ImportError:
    try:
        import Image
    except ImportError:
        nuke.message("Can't import PIL module, please run 'pip install Pillow'")
        raise BaseException

def check_script(name):
    """
    :type name: Script name that is checked against regular expression
    """
    re1='((?:[a-z][a-z]*[0-9]+[a-z0-9]*))'  # Shot
    re2='(\\.)'                             # .
    re3='((?:[a-z][a-z]+))'                 # Task
    re4='(\\.)'                             # .
    re5='((?:[a-z][a-z]+))'                 # Artist
    re6='(\\.)'                             # .
    re7='(v)'                               # v
    re8='(\\d+)'                            # Major version number
    re9='(\\.)'                             # .
    re10='(\\d+)'                           # Minor version number
    re11='(\\.)'                            # .
    re12='(nk)'                             # nk
    rg = re.compile(re1+re2+re3+re4+re5+re6+re7+re8+re9+re10+re11+re12,re.IGNORECASE|re.DOTALL)
    result = rg.match(name)
    return result


def init_common_vars(snapsDir=None):
    """
    Initialize common variables used in other functions
    :rtype : dictionary
    :param snapsDir: Script root directory + /snaps
    :return: Dict with all common variables
    """
    all_vars = {}
    scriptPath = nuke.toNode('root').knob('name').value()
    scriptName = scriptPath.split("/")[-1]
    timestamp = time.strftime("%d-%m-%Y") + '_' + time.strftime("%H-%M")
    snapPath = snapsDir + '/' + scriptName + '_' + timestamp
    snapScriptName = snapPath + "/" + scriptName + '_' + timestamp + '.nk'
    snapImageFile = snapPath + "/" + scriptName + '_' + timestamp + '.jpg'
    snapCommentFile = snapPath + "/" + scriptName + '_' + timestamp+ '.txt'
    currentFrame = int(nuke.frame())
    fakeFrameRange = str(currentFrame) + "-" + str(currentFrame)
    writeUniqueName = "tmp_Snapshotr" + timestamp
    nodeLabel = "<b>SNAP</b><br />" + str(time.strftime("%d-%m-%Y")).replace(
            "-", ".") + ' ' + str(time.strftime("%H-%M")).replace("-", ":")
    all_vars.update({"scriptPath":scriptPath, "scriptName":scriptName, "timestamp":timestamp, "snapPath":snapPath,
                 "snapScriptName":snapScriptName, "snapImageFile":snapImageFile, "snapCommentFile":snapCommentFile,
                 "currentFrame":currentFrame, "fakeFrameRange":fakeFrameRange, "writeUniqueName":writeUniqueName,
                 "nodeLabel":nodeLabel})
    return all_vars


def create_snapshot_dirs(rootDir=None, snapsDir=None, snapPath=None, markNode=None):
    """
    Create snapsDir and individual directory for a snapshot inside it
    :param rootDir: Where .nk file is saved
    :param snapsDir: Script root directory + /snaps
    :param snapPath: Path to directory where snapshot .nk is stored
    """
    try:
        if rootDir != "" and snapsDir != "":
            if not os.path.exists(snapsDir):
                os.makedirs(snapsDir)
                print "\n~ Created root snapshots dir: " + snapsDir
        else:
            nuke.message("Please save your script")
            raise BaseException
        if not os.path.exists(snapPath):
            os.makedirs(snapPath)
            print "\n ------------ Snap @ " + time.strftime("%H:%M") + " ------------"
            print "\n~ Created snapshot directory: " + snapPath
        else:
            print "\n! Snapshot failed, directory exists"
            nuke.message('Snapshot failed, directory exist')
            raise BaseException
    except ValueError:
            nuke.message("'Mark node' is checked, but no node selected")
            raise BaseException


def create_snapshot_script(scriptPath=None, snapScriptName=None, upversion=None):
    """
    Writes snapshot .nk script
    :param scriptPath: Path to the snapshot directory where .nk is stored
    :param snapScriptName: Absolute path to the .nk
    :param upversion: if True, minor version +1 (e.g v01.00 --> v01.01)
    """
    try:
        tmpScriptPath = scriptPath
        if upversion:
            up_minor_version = int(scriptPath.split("/")[-1].split(".")[-2]) + 1
            up_script_name = ".".join(tmpScriptPath.split("/")[-1].split(".")[:-2]) + "." \
                             + str(up_minor_version).zfill(2) + ".nk"
            tmpScriptPath = "/".join(tmpScriptPath.split("/")[:-1]) + "/" + up_script_name
        print "\n~ Writing script: " + str(snapScriptName)
        nuke.scriptSaveAs(str(snapScriptName))
        os.chmod(snapScriptName, 0444)
        rootNode = nuke.toNode('root')
        rootNode.knob('name').setValue(tmpScriptPath)
        nuke.scriptSave()
    except:
        nuke.message("\n! Can't save the script, no snapshot created")
        raise BaseException


def create_snapshot_comment(snapCommentFile=None, commentText=None):
    """
    Writes .txt file with comment provided by user
    :param snapCommentFile: Absolute path to the .txt
    """
    try:
        snapCommentFileObj = open(snapCommentFile, "w+")
        snapCommentFileObj.write(commentText)
        snapCommentFileObj.close()
        os.chmod(snapCommentFile, 0444)
        print "\n~ Writing text comment: " + snapCommentFile
    except:
        print "\n! Writing comment failed"


def create_snapshot_screenshot(DEV=None, snapImageFile=None):
    """
    Writes screenshot of currrent viewer and 100px thumbnail from it, chmod 444 both
    :param DEV: Debug level
    :param snapImageFile: Absolute path to .jpeg
    """
    if DEV > 0:
        import threading
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
    print "\n~ Writing autosnap screenshot: " + str(snapImageFile)


def label_node(markNode=None, nodeLabel=None):
    """
    Mark selected node with color and label with timestamp
    :param markNode: markNode knob from python panel
    :param nodeLabel: timestamp label
    """
    if markNode.value() is True:
        initial_node = nuke.selectedNodes()[0]
        if initial_node.Class() == "Viewer":
            initial_node.setSelected(False)
            initial_node = initial_node.dependencies()[-1]
            initial_node.setSelected(True)
        try:
            nuke.selectedNode()
            nuke.selectedNode().knob('tile_color').setValue(112233)
            nuke.selectedNode().knob('label').setValue(nodeLabel)
        except ValueError:
            nuke.message("'Mark node' is checked, but no node selected")
            raise BaseException


def copy_viewer_input(node=None):
    """
    :param node: viewerInput
    :return: copy of current Viewer input
    """
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


def create_snapshot_fullres(snapImageFile=None, writeUniqueName=None, fakeFrameRange=None):
    """
    Check if input process and viewer input are valid, bake LUT, write full-res image, thumbnail, chmod 0444 both
    :param snapImageFile: Absolute path to .jpeg
    :param writeUniqueName: name of temporarily Write node
    :param fakeFrameRange: current frame X represented as "X-X"
    """
    try:
        initial_node = nuke.selectedNodes()[0]
        if initial_node.Class() == "Viewer":
            initial_node.setSelected(False)
            initial_node = initial_node.dependencies()[-1]
            initial_node.setSelected(True)
    except IndexError:
        nuke.message("Select node from which to render full-res snapshot")
        raise BaseException
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
        initial_node.setSelected(False)
        tmpViewerProcess.setSelected(True)
        initial_node = nuke.selectedNodes()[0]
    else:
        print "\n! No valid IP attached to the Viewer, going on..."
    if 'Node' in str(type(viewerInput)) or 'Gizmo' in str(type(viewerInput)):
        is_ip_valid = True
        newIp = copy_viewer_input(viewerInput)
        tmpViewerInput = nuke.toNode(newIp.name())
        tmpViewerInput.setInput(0, nuke.selectedNode())
        initial_node.setSelected(False)
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


def write_html(pFile=None, html=None):
    """
    :param pFile: Full path to .html
    :param html: content to write
    """
    pageFile = open(pFile, "w+")
    pageFile.writelines(html)
    pageFile.close()
