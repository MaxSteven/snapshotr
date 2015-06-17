#
# This should be launched from the python interpreter that is shipped with Nuke assuming it has py.test installed
#

import os
from .snapshotr_settings import *
import snapshotr_common as cmn

class TestCommons:
    def test_correct_installation(self):
        assert os.path.exists(SS_PATH)
        assert os.path.isfile(SS_PATH + "/markup.py")
        assert os.path.isfile(SS_PATH + "/scandir.py")
        assert os.path.isfile(SS_PATH + "/snapshotr_webview.py")
        assert os.path.isfile(SS_PATH + "/snapshotr_panel.py")
        assert os.path.isfile(SS_PATH + "/snapshotr_common.py")

    def test_script_name_checking(self):
        assert cmn.check_script("ss0001.comp.username.v01.00.nk") is not None
        assert cmn.check_script("ss0001.comp-user.v01.00.nk") is None