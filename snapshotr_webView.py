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
import pwd
from sys import path
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
path.append(snapr_path)
import markup, scandir

def updateWebView(debug=0, s_dirs=None):
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
    print debug
    snapsIterator = scandir.walk(s_dirs)
    dirList = []
    for directory in snapsIterator:
        dirList.append(directory)

    if debug > 1:
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

    if debug > 1:
        print "\n ------------------------------ "
        print "* scriptName: " + scriptName
        print "* rootDir: " + rootDir

    if debug > 1:
        print "\n ------------------------------ "
        print "* scriptName: " + scriptName
        print "* snapsList: " + str(snapsList)

    txtList = []
    userList = []

    # because os.stat() inside class crashes Nuke,
    # we are constructing bicycle here
    c = 0
    for ROOT, DIR, FILES in scandir.walk(s_dirs):
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

    if debug > 1:
        print "\n ------------------------------ "
        for index, item in enumerate(txtList):
            print "* txtList: " + str(index) + " = " + str(item)

    for x in txtList:
        if os.path.exists(x) is True:
            userOwner = pwd.getpwuid(os.stat(x).st_uid).pw_name
            userList.append(userOwner)
        else:
            pass

    if debug > 1:
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
