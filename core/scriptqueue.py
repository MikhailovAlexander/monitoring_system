import logging
import logging.config
import tkinter as tk
import datetime
# from queue import Queue
import threading

from core.scriptplugin import ScriptPlugin

EXECUTE = 2
FAIL = 3
CANCEL = 4

NOT_ACTIVE = 0
ACTIVE = 1
CHECK = 2


class QueueItem(object):
    """Class for queue item"""

    def __init__(self, driver, log_config, script, script_id, fact_check_id):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Creating QueueItem")
        self._driver = driver
        self._script = script
        self._script_id = script_id
        self._fact_check_id = fact_check_id

    @property
    def fact_check_id(self):
        """Returns identifier from fact_check table"""
        return self._fact_check_id

    @property
    def script_id(self):
        """Returns identifier from script table"""
        return self._script_id

    def _upd_fact_check_fail(self):
        self._driver.fact_check_upd(self._fact_check_id,
                                    datetime.datetime.now(),
                                    fact_check_obj_count=None,
                                    fact_check_status_id=FAIL)

    def run_and_save(self):
        status = self._driver.fact_check_rd_status(self._fact_check_id)
        if not status or status == CANCEL:
            return
        test = False
        try:
            test = self._script.test()
        except Exception as ex:
            self._logger.exception(ex)
        if not test:
            self._logger.error("Test script failed. "
                               f"script_id: {self._script_id}")
            self._upd_fact_check_fail()
            return
        result = []
        try:
            result = self._script.run()
        except Exception as ex:
            self._logger.exception(ex)
            self._upd_fact_check_fail()
            return
        if not result:
            self._driver.fact_check_upd(self._fact_check_id,
                                        datetime.datetime.now(),
                                        fact_check_obj_count=None,
                                        fact_check_status_id=EXECUTE)
            return
        self._driver.begin_transaction()
        try:
            self._driver.fact_check_upd(self._fact_check_id,
                                        datetime.datetime.now(),
                                        fact_check_obj_count=result[0],
                                        fact_check_status_id=EXECUTE)
            self._driver.object_ins(result[1])
            self._driver.commit()
        except Exception as ex:
            self._logger.exception(ex)
            self._driver.rollback()
            raise RuntimeError(f"Error during check result saving: {ex}")


class ScriptQueue(object):
    """Class for script running manage"""

    def __init__(self, driver, log_config, iv_current_script):
        self._log_config = log_config
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Creating ScriptQueue")
        self._state = tk.IntVar(value=NOT_ACTIVE)
        self._state.trace("w", self._on_upd_state)
        self._current_script = iv_current_script
        # self._queue = Queue()
        self._driver = driver
        self._scr_plug = ScriptPlugin(log_config,
                                      self._config["script_plugin_conf"],
                                      self._driver)

    @property
    def state(self):
        """Returns active state of queue as a bool value"""
        return bool(self._state.get())

    @property
    def current_script(self):
        """Returns current script identifier"""
        return self._current_script.get()

    def _on_upd_state(self):
        state = self._state.get()
        if state == ACTIVE or state == CHECK:
            return
        threading.Thread(target=self._refresh_queue, daemon=True).start()

    def _refresh_queue(self):
        self._state.set(CHECK)
        items = []
        try:
            items = self._get_check_que_db()
        except Exception as ex:
            self._state.set(NOT_ACTIVE)
            self._logger.exception(ex)
            raise RuntimeError(f"Error during checks search: {ex}")
        if not items:
            self._state.set(NOT_ACTIVE)
            return
        self._state.set(ACTIVE)
        for item in items:
            self._current_script.set(item.script_id)
            item.run_and_save()
        self._current_script.set(None)
        self._state.set(NOT_ACTIVE)

    def _get_check_que_db(self):
        checks = self._driver.fact_check_que()
        items = []
        for check in checks:
            try:
                script = self._scr_plug.get_script(check[1])
                items.append(QueueItem(self._driver, self._log_config, script,
                                       check[1], check[0]))
            except Exception as ex:
                self._logger.exception(ex)
                self._driver.fact_check_upd(check[0], datetime.datetime.now(),
                                            fact_check_obj_count=None,
                                            fact_check_status_id=FAIL)
        return items

