import logging
import logging.config
import datetime

QUEUE = 1
EXECUTE = 2
FAIL = 3
CANCEL = 4


class QueueItem(object):
    """Class for queue item"""

    def __init__(self, log_config, script, script_id, fact_check_id):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Creating QueueItem")
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

    @property
    def script_name(self):
        """Returns script name from file"""
        return self._script.name

    def run_and_save(self, driver):
        """Runs script and save results in db

        :param driver - db_driver to save results
        :return void

        """
        test = False
        try:
            status = driver.fact_check_rd_status(self._fact_check_id)
            if not status or status[0] == CANCEL:
                return
            test = self._script.test()
        except Exception as ex:
            self._logger.exception(ex)
        if not test:
            self._logger.error("Test script failed. "
                               f"script_id: {self._script_id}")
            driver.fact_check_upd(self._fact_check_id,
                                  datetime.datetime.now(),
                                  fact_check_obj_count=None,
                                  fact_check_status_id=FAIL)
            return
        result = []
        try:
            result = self._script.run(self._fact_check_id)
        except Exception as ex:
            self._logger.exception(ex)
            driver.fact_check_upd(self._fact_check_id,
                                  datetime.datetime.now(),
                                  fact_check_obj_count=None,
                                  fact_check_status_id=FAIL)
            return
        if not result:
            driver.fact_check_upd(self._fact_check_id,
                                  datetime.datetime.now(),
                                  fact_check_obj_count=None,
                                  fact_check_status_id=EXECUTE)
            return
        driver.begin_transaction()
        try:
            driver.fact_check_upd(self._fact_check_id,
                                  datetime.datetime.now(),
                                  fact_check_obj_count=result[0],
                                  fact_check_status_id=EXECUTE)
            driver.object_ins(result[1])
            driver.commit()
        except Exception as ex:
            self._logger.exception(ex)
            driver.rollback()
            driver.fact_check_upd(self._fact_check_id,
                                  datetime.datetime.now(),
                                  fact_check_obj_count=None,
                                  fact_check_status_id=FAIL)


class ScriptQueue(object):
    """Class for script running manage"""

    def __init__(self, driver, log_config, script_plugin, queue):
        self._log_config = log_config
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info("Creating ScriptQueue")
        self._queue = queue
        self._driver = driver
        self._scr_plug = script_plugin
        self._fill_from_db()

    def clean(self):
        """Extracts all checks from the queue

        :return void

        """
        while not self._queue.empty():
            self._queue.get()

    def clean_and_cancel(self):
        """Extracts all checks from the queue and set cancel status

        :return void

        """
        items = []
        while not self._queue.empty():
            items.append(self._queue.get())
        self._logger.debug(f"{items}")
        for item in items:
            try:
                status = self._driver.fact_check_rd_status(item.fact_check_id)
                if status:
                    if status[0] == QUEUE:
                        self._driver.fact_check_upd(item.fact_check_id,
                                                    datetime.datetime.now(),
                                                    fact_check_obj_count=None,
                                                    fact_check_status_id=CANCEL)
            except Exception as ex:
                self._logger.exception(ex)

    def refresh_from_db(self, current_check_id=None):
        """Cleans queue and fills it from db"""
        self.clean()
        self._fill_from_db(current_check_id)

    def put(self, script_id, link_id):
        """Checks script and puts it to the queue

        :param script_id - script table record identifier
        :param link_id - user_script_link table record identifier
        :return void

        """
        script = None
        try:
            script = self._scr_plug.get_script(script_id)
        except Exception as ex:
            self._logger.exception(ex)
            raise RuntimeError(f"Ошибка чтения скрипта: {script_id}")
        try:
            fact_check_id = self._driver.fact_check_ins(datetime.datetime.now(),
                                                        link_id)
        except Exception as ex:
            self._logger.exception(ex)
            raise RuntimeError("Ошибка сохранения проверки в бд "
                               f"(скрипт: {script_id})")
        self._queue.put(QueueItem(self._log_config, script, script_id,
                                  fact_check_id))

    def _fill_from_db(self, current_check_id=None):
        try:
            items = self._get_check_que_db()
        except Exception as ex:
            self._logger.exception(ex)
            raise RuntimeError(f"Error during checks search: {ex}")
        for item in items:
            if item.fact_check_id != current_check_id:
                self._queue.put(item)

    def _get_check_que_db(self):
        checks = self._driver.fact_check_que()
        items = []
        for check in checks:
            try:
                script = self._scr_plug.get_script(check[1])
                items.append(QueueItem(self._log_config, script, check[1],
                                       check[0]))
            except Exception as ex:
                self._logger.exception(ex)
                self._driver.fact_check_upd(check[0], datetime.datetime.now(),
                                            fact_check_obj_count=None,
                                            fact_check_status_id=FAIL)
        return items
