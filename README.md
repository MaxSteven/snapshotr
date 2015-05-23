## What is it?
This is a Nuke snapshot manager which is used to make script versioning more straightforward

## What is snapshot?
It is a backup of script at the specific time with user comment and screenshot  
All snapshots are presented in user friendly web-interface

## Installation
1. `cd ~/.nuke && git clone https://github.com/artaman/snapshotr.git`
2. Open `~/.nuke/init.py` with your favourite editor
3. Add the following code:

```python
#
# Snapshotr
#
import os, nuke
snapr_path = os.getenv("HOME") + "/.nuke"
if os.path.exists(snapr_path + "/snapshotr"):
    nuke.pluginAddPath(snapr_path)
    print "~ Loading Snapshotr into the Nuke..."
    import snapshotr
else:
    print "! Snapshotr path can't be found, going on..."
```

## File versioning
This tool assumes that artist uses the following convention in naming scripts: *shot.user.task.v01.00.nk*  
In case file is saved with incorrect name, it will display a warning message and panel will not load  
Each snapshot increases minor version by one (e.g v01.00 --> v01.01)

## Nuke panel
After following steps above you will have a new panel called "Snapshotr"  
By default it is dockable, but it can be dragged out and used as a modal window:

![snapshotr_main](https://cloud.githubusercontent.com/assets/300146/5570169/83b73a34-8fb8-11e4-8f45-42d25097a31b.png)
* __Comment field__ — Self-descriptive. Color can be specified as a hashtag (#green, #blue, etc)
* __Instant__ — Makes snapshot using screenshot of current viewer, perceptually instant for a user
* __Full__ — Makes full-res snapshot, image is rendered in background from the selected node. Custom LUT's are handled correctly. Whatever you have as input\_process or/and viewer_process
will be converted to sRGB prior to render
* __Open__ — Opens new browser tab with web-view
* __Autosnap__ – Creates automatic instant snapshot every XX minutes
* __Mark node__ — Marks selected node with color and current timestamp

## Web view
Here is an example of a web page generated each time user manually initiated snapshot creation:

![v020_webview](https://cloud.githubusercontent.com/assets/300146/7670598/dbf51c0c-fcdc-11e4-9b2d-af5d08e9703c.png)

By default snapshots are sorted from new to old, this can be changed by clicking "Time created" column header. Clicking "nk" button user can see a box with path to the .nk script. Clicking the image thumbnail, full-res version will be opened (limited to the screen width).

## File structure
![v020_filelist](https://cloud.githubusercontent.com/assets/300146/7670600/30f23a6e-fcdd-11e4-870e-fcff797d8232.png)

Snapshots created in "snaps" directory that is relative to the current script path. So, if script is /projects/xxx/abc001.john.comp.v01.00.nk, then snapshots will be stored in /projects/xxx/snaps/   
After writing files to the filesystem they are chmod'ed to 0444  

## Debugging
![v020_debug](https://cloud.githubusercontent.com/assets/300146/7670615/bd4a68e2-fcdd-11e4-940d-21498f9686ab.png)

Snapshotr outputs reasonable amount of information to the Nuke script editor  
If you want more, change ```DEV``` variable to 1 or 2 (last one will output a lot)

## Performance
To be tested with v0.2.0
