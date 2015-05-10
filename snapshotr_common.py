import re
import nuke
import time
import os
from PIL import Image

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
    all_vars.update({"scriptPath":scriptPath, "scriptName":scriptName, "timestamp":timestamp, "snapPath":snapPath,
                 "snapScriptName":snapScriptName, "snapImageFile":snapImageFile, "snapCommentFile":snapCommentFile})
    return all_vars

def create_snapshots_root(rootDir=None, snapsDir=None, snapPath=None):
    """
    Create snapsDir and individual directory for a snapshot inside it
    :param rootDir: Where .nk file is saved
    :param snapsDir: Script root directory + /snaps
    :param snapPath: Path to directory where snapshot .nk is stored
    """
    if rootDir != "" and snapsDir != "":
        if not os.path.exists(snapsDir):
            os.makedirs(snapsDir)
            print "\n~ Created root snapshots dir: " + snapsDir
    else:
        nuke.message("Please save your script")
    if not os.path.exists(snapPath):
        os.makedirs(snapPath)
        print "\n ------------ Autosnap @ " + time.strftime("%H:%M") + " ------------"
        print "\n~ Created autosnap dir: " + snapPath
    else:
        print "\n! Autosnap failed, directory exists"

def create_snapshot_script(scriptPath=None, snapScriptName=None):
    """
    Writes snapshot .nk script
    :param scriptPath: Path to the snapshot directory where .nk is stored
    :param snapScriptName: Absolute path to the .nk
    """
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

def create_snapshot_comment(snapCommentFile=None):
    """
    Writes .txt file with comment provided by user
    :param snapCommentFile: Absolute path to the .txt
    """
    try:
        snapCommentFileObj = open(snapCommentFile, "w+")
        commentText = "#autosnap"
        snapCommentFileObj.write(commentText)
        snapCommentFileObj.close()
        os.chmod(snapCommentFile, 0444)
        print "\n~ Writing text comment (auto): " + snapCommentFile
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