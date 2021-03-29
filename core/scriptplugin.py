import logging
import logging.config
import os
import fnmatch
import hashlib
import datetime

from core.basescript import BaseScript
from core.dynamicimport import DynamicImport


class ScriptPlugin(object):
    """Class for managing scripts"""

    def __init__(self, log_config, config, driver):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info('Creating ScriptPlugin')
        self._folder = config["folder"]
        self._prefix = config["prefix"]
        self._driver = driver

    def _get_script(self, file_name):
        path = os.path.join(self._folder, file_name)
        if not os.path.exists(path):
            raise RuntimeError(f"File is not exists: {path}")
        cls_name = file_name.replace(".py", "")
        mod_name = ".".join([os.path.basename(self._folder), cls_name])
        return DynamicImport.get_object(self._logger, mod_name, cls_name,
                                        BaseScript)

    @staticmethod
    def _get_hash(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            script_text = file.read()
        return hashlib.sha256(script_text.encode()).digest()

    @staticmethod
    def _hash_check(file_path, hash_code):
        with open(file_path, 'r', encoding="utf-8") as file:
            script_text = file.read()
        file_hash = hashlib.sha256(script_text.encode()).digest()
        return file_hash == hash_code

    def search_scripts(self):
        """

        :return: List of new scripts in target folder
        """
        script_names = set([row[1] + '.py'
                            for row in self._driver.script_rda()])
        new_scripts = []
        file_names = set([file for file in os.listdir(self._folder)
                         if fnmatch.fnmatch(file, self._prefix + '*.py')])
        files = file_names - script_names
        for file in files:
            cls_name = file.replace(".py", "")
            mod_name = ".".join([os.path.basename(self._folder), cls_name])
            try:
                script = DynamicImport.get_object(self._logger, mod_name,
                                                  cls_name, BaseScript)
                test = script.test()
                new_scripts.append([file, script.name, script.description,
                                    script.author, "готов" if test
                                    else "не готов"])
            except Exception as ex:
                self._logger.exception(f"Script import error file: {file}")
                self._logger.exception(ex)
        return new_scripts

    def get_actual_scripts(self, limit, offset, user_id=None):
        """

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :param user_id: identifier from table user for checking availability
        :return: List of actual scripts which are available to the user
        """
        scripts = self._driver.script_rd_pg(limit, offset, user_id)
        scripts = [[*row, None] for row in scripts]  # Status column is added
        for script in scripts:
            status = "Проверен"
            file = script[2] + ".py"
            path = os.path.join(self._folder, file)
            if not os.path.exists(path):
                status = "Файл скрипта не найден"
            elif not ScriptPlugin._hash_check(path, script[0]):
                status = "Файл скрипта изменен"
            script[7] = status
        return [script[1:] for script in scripts]

    def save_script(self, file_name):
        """
        Saves new script in db

        :param file_name: script file name
        :return: void
        """
        path = os.path.join(self._folder, file_name)
        script = self._get_script(file_name)
        self._driver.script_ins(script.name, script.description, script.author,
                                datetime.datetime.now(),
                                ScriptPlugin._get_hash(path),
                                script.object_type.value)

    def update_script(self, script_id):
        """
        Updates script in db

        :param script_id: script table record identifier
        :return: void
        """
        script_rec = self._driver.script_rd(script_id)
        file_name = script_rec[1] + ".py"
        self._logger.debug(f"cwd: {os.getcwd()}")
        path = os.path.join(self._folder, file_name)
        script = self._get_script(file_name)
        self._driver.script_upd(script_id, script.name, script.description,
                                script.author, ScriptPlugin._get_hash(path),
                                script.object_type.value)

    def delete_script(self, script_id):
        """
        Delete script in db

        :param script_id: script table record identifier
        :return: void
        """
        self._driver.script_del(script_id, datetime.datetime.now())

    def get_script(self, script_id):
        """

        :param script_id: script table record identifier
        :return: script object
        """
        script_rec = self._driver.script_rd(script_id)
        file_name = script_rec[1] + ".py"
        path = os.path.join(self._folder, file_name)
        script = self._get_script(file_name)
        if self._hash_check(path, script_rec[5]):
            return script
        else:
            raise RuntimeError(f"Hash code check was failed: {path}")


