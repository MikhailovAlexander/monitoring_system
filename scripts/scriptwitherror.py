import os
import sys
import fnmatch
import datetime

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from core.basescript import BaseScript, ObjectType, ErrorLevel, CheckObject


class scriptwitherror(BaseScript):
    """Test script example for design script module"""

    def __init__(self):
        self._obj_type = ObjectType.FILE
        self._checked_obj_cnt = 0
        self._results = []

    def test(self):
        """Checks resources which is used by script

        :return bool value

        """
        return True

    def run(self, fact_check_id):
        """Runs script

        :param fact_check_id - fact_check table record identifier
        :return Count of checked objects and script results (set of records)
        """
        raise RuntimeError("Script failed")

    @property
    def name(self):
        """Returns script name"""
        return "scriptwitherror"

    @property
    def description(self):
        """Returns script description"""
        return "test script example for design script module"

    @property
    def author(self):
        """Returns script author"""
        return "Mikhailov A"

    @property
    def object_type(self):
        """Returns script results type"""
        return self._obj_type


if __name__ == "__main__":
    scr = scripttest()
    print(scr.run())
