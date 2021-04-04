import logging
import logging.config
import json
import threading
from queue import Queue

from forms.mainform import MainForm
from db.basedbdriver import BaseDbDriver
from core.dynamicimport import DynamicImport

LOG_CONF_FILE_PATH = './core/logger_conf.json'
APP_CONF_FILE_PATH = './core/app_conf.json'


def load_json(json_file_path):
    """Reads data from a json-file"""
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)


def get_logger(log_conf):
    """

    :param log_conf - logger settings dictionary
    :return logger object

    """
    logging.config.dictConfig(log_conf)
    return logging.getLogger(__name__)


def queue_handle(_tk_queue, _queue, _logger, _db_mod_name, _db_cls_name,
                 _base_db_driver, _log_config, _db_config):
    """Script queue handle for running scripts in separated thread"""
    logger.debug("queue_handle is running")
    queue_driver = DynamicImport.get_object(_logger, _db_mod_name, _db_cls_name,
                                            _base_db_driver,
                                            log_config=_log_config,
                                            db_config=_db_config)
    queue_driver.get_connection()
    try:
        while _tk_queue.empty():
            pass
        root_vars = _tk_queue.get()
        sv_check_name = root_vars[0]
        iv_check_id = root_vars[1]
        sv_check_name.set("Текущая проверка: отсутствует")
        iv_check_id.set(-1)
        while True:
            item = _queue.get()
            sv_check_name.set(f"Текущая проверка: скрипт {item.script_name}")
            iv_check_id.set(item.fact_check_id)
            item.run_and_save(queue_driver)
            _queue.task_done()
            if _queue.empty():
                sv_check_name.set("Текущая проверка: отсутствует")
                iv_check_id.set(-1)
    finally:
        queue_driver.close_connection()


log_config = load_json(LOG_CONF_FILE_PATH)
logger = get_logger(log_config)
logger.info('logger was created')

app_config = load_json(APP_CONF_FILE_PATH)
logger.info('App config was read')
db_conf = app_config["db_conf"]
db_mod_name = db_conf["db_driver_module"]
db_cls_name = db_conf["db_driver_class"]
driver = DynamicImport.get_object(logger, db_mod_name, db_cls_name,
                                  BaseDbDriver, log_config=log_config,
                                  db_config=db_conf)
if not driver.is_db_exist():
    logger.info('DB is not exist')
    driver.init_db()
    logger.info('DB was created')
driver.get_connection()
logger.info('DB connection was opened')

scr_queue = Queue()
root_queue = Queue()
thread = threading.Thread(target=queue_handle, args=(root_queue, scr_queue,
                                                     logger, db_mod_name,
                                                     db_cls_name, BaseDbDriver,
                                                     log_config, db_conf),
                          daemon=True)

scr_queue.join()
root_queue.join()

root = MainForm(driver, log_config, app_config["main_form_conf"], scr_queue)
root.geometry("1200x700")
root_queue.put([root.sv_current_check_name, root.iv_current_check_id])
thread.start()

logger.info('MainForm was started')
root.mainloop()
logger.info('MainForm was closed')
driver.close_connection()
logger.info('DB connection was closed')
