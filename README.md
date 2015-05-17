## What is it?
This is a Nuke snapshot manager used to make script versioning more straightforward.

## What is snapshot?
It is a backup of script at the specific time with user comment and screenshot.  
All snapshots are presented in user friendly web-interface.

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
This tool assumes that artist use the following convention in naming scripts: *shot.user.task.v01.00.nk*   
In case file is saved with incorrect name, it will display a warning message and panel will not load  
Each snapshot increase minor version by one (e.g v01.00 --> v01.01)

## Nuke panel
After following steps above you will have a new panel called "Snapshotr".  
By default it is dockable, but can be dragged out and used as a modal window:

![snapshotr_main](https://cloud.githubusercontent.com/assets/300146/5570169/83b73a34-8fb8-11e4-8f45-42d25097a31b.png)
* __Comment field__ — Self-descriptive. Color can be specified as a hashtag (#green, #blue, etc).
* __Instant__ — Make snapshot using screenshot of current viewer, perceptually instant for a user.
* __Full__ — Make full-res snapshot, image is rendered in background from selected node.  
Custom LUT's handled correctly. Whatever you have as input\_process or/and viewer_process  
will be converted to sRGB prior to render.  
* __Open__ — Open new browser tab with web-view  
* __Autosnap__ – Create automatic instant snapshot every XX minutes  
* __Mark node__ — Mark selected node with color and current timestamp

## Web view
Here is an example of web page generated each time user manually initiate snapshot creation:

![web-view-new](https://cloud.githubusercontent.com/assets/300146/5579102/40f3f062-9070-11e4-8da9-5dc5aa995981.jpg)

By default snapshots are sorted from new to old, this can be changed by clicking "Time created" column header.  
Clicking "nk" button user can see a box with path to the .nk script. Clicking the image thumbnail, full-res version will be opened (limited to the screen width).

## File structure
![snaps_filestruct](https://cloud.githubusercontent.com/assets/300146/5579347/ce3d1aea-9073-11e4-90e8-3c916391991e.png)

Snapshots created in "snaps" directory that is relative to the current script path.  
So, if script is /projects/xxx/abc001.john.comp.v01.00.nk, then snapshots will be stored in /projects/xxx/snaps/  
After writing files to the filesystem they are chmod'ed to 0444.

## Debugging
![script_editor](https://cloud.githubusercontent.com/assets/300146/5579110/65096d9c-9070-11e4-91ab-7eb2c63b778a.png)

Snapshotr output reasonable amount of information to the Nuke script editor.  
If you want more, change ```DEV``` variable to 1 or 2 (last one will output _a lot_).

## Performance

On typical workstation this tool parse ~200 snapshots to the web-view per second.
