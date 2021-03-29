import os
import sys
import fnmatch
import datetime

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
from core.basescript import BaseScript, ObjectType, ErrorLevel, CheckObject


class scripttest(BaseScript):
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

    def run(self):
        """Runs script

        :return Count of checked objects and script results (set of records)
        """
        target_dir = os.path.dirname(os.path.dirname(__file__))
        for folder, subfolders, files in os.walk(target_dir):
            for file in files:
                path = os.path.abspath(os.path.join(folder, file))
                el = ErrorLevel.WARNING
                if fnmatch.fnmatch(file, '*.py'):
                    el = ErrorLevel.TRIVIAL
                if "\." not in folder:
                    obj = CheckObject(file, path, None, None,
                                      datetime.datetime.fromtimestamp(
                                          os.path.getmtime(path)),
                                      el)
                    self._results.append(obj.to_db_row())
                self._checked_obj_cnt += 1
        return [self._checked_obj_cnt, self._results]

    @property
    def name(self):
        """Returns script name"""
        return "scripttest"

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
