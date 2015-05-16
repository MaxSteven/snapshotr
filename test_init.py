import os
from . import snapr_path
import snapshotr_common as cmn

class TestCommons:
    def test_correct_installation(self):
        assert os.path.exists(snapr_path)
        assert os.path.isfile(snapr_path + "/markup.py")
        assert os.path.isfile(snapr_path + "/scandir.py")
        assert os.path.isfile(snapr_path + "/snapshotr_webview.py")
        assert os.path.isfile(snapr_path + "/snapshotr_panel.py")
        assert os.path.isfile(snapr_path + "/snapshotr_common.py")

    def test_script_name_checking(self):
        assert cmn.check_script("ss0001.comp.username.v01.00.nk") is not None
        assert cmn.check_script("ss0001.comp-user.v01.00.nk") is None



