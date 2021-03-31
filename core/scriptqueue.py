import logging
import logging.config
from multiprocessing import Process
import datetime
from queue import Queue

from core.scriptplugin import ScriptPlugin

EXECUTE = 2
FAIL = 3
CANCEL = 4


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

    def __init__(self, driver, log_config, script_plugin_conf, iv_current_check):
        self._log_config = log_config
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Creating ScriptQueue")
        self._current_check = iv_current_check
        self._queue = Queue()
        self._process = Process(target=self._queue_handle, daemon=True)
        self._driver = driver
        self._scr_plug = ScriptPlugin(log_config, script_plugin_conf, driver)
        self._launch_queue()

    @property
    def current_check(self):
        """Returns current script identifier"""
        return self._current_check.get()

    def put(self, script, script_id, fact_check_id):
        """puts new script to the queue
        and start handler if it is not working
        """
        self._queue.put(QueueItem(self._driver, self._log_config, script,
                                  script_id, fact_check_id))
        if not self._process.is_alive():
            self._process.start()

    def stop_queue(self):
        """Stop queue handler if it is working"""
        if self._process.is_alive():
            self._process.terminate()

    def stop_check(self, fact_check_id):
        """Restart queue handler if it is working and needs check is running"""
        if self._process.is_alive() and self._current_check == fact_check_id:
            self._process.terminate()
            self._process.start()

    def refresh(self):
        """Clears queue, reload it from db and restart handler"""
        self._launch_queue()

    def _queue_handle(self):
        self._logger.debug("queue_handle is running")
        while not self._queue.empty():
            item = self._queue.get()
            self._current_check.set(item.fact_check_id)
            item.run_and_save()
        self._current_check.set(None)

    def _launch_queue(self):
        if self._process.is_alive():
            self._process.terminate()
        self._queue = Queue()
        items = []
        try:
            items = self._get_check_que_db()
        except Exception as ex:
            self._logger.exception(ex)
            raise RuntimeError(f"Error during checks search: {ex}")
        for item in items:
            self._queue.put(item)
        self._process.start()

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
