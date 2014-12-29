Snapshotr
=========

Snapshotr is a Nuke snapshot manager used to make script versioning more straightforward and user friendly.

To start with:

1. `cd ~/.nuke && git clone https://github.com/artaman/snapshotr.git`
2. Open `~/.nuke/init.py` with your favourite editor
3. Add the following code:

```python
#
# Snapshotr
#
import os, nuke
snapr_path = os.getenv("HOME") + "/.nuke/snapshotr"
if os.path.exists(snapr_path):
    nuke.pluginAddPath(snapr_path)
    print "~ Loading Snapshotr into the Nuke..."
    import snapshotr
else:
    print "! Snapshotr path can't be found, going on..."
```

After doing so you will have a new panel called "Snapshotr".  
By default it is dockable but can be dragged out and used as modal window.

![snapshotr_main](https://cloud.githubusercontent.com/assets/300146/5570169/83b73a34-8fb8-11e4-8f45-42d25097a31b.png)

__comment field__ — Self-descriptive. You can add color as hashtag (#green, #blue, etc).  
__Instant__ — Make snapshot using screenshot of current viewer, perceptually instant for a user.  
__Full__ — Make full-res snapshot, image is rendered in background from selected node.  
__Open__ — Open new firefox tab with web-view.  
__mark node__ — Mark selected node with color and current timestamp.


