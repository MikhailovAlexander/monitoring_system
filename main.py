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
    """Read data from json-file"""
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)


def get_logger(log_conf):
    """

    :param log_conf - logger settings dictionary
    :return logger object

    """
    logging.config.dictConfig(log_conf)
    return logging.getLogger(__name__)


def queue_handle(_queue, _logger, _db_mod_name, _db_cls_name, _base_db_driver,
                 _log_config, _db_config):
    """Script queue handle for running scripts in separated thread"""
    logger.debug("queue_handle is running")
    queue_driver = DynamicImport.get_object(_logger, _db_mod_name, _db_cls_name,
                                            _base_db_driver,
                                            log_config=_log_config,
                                            db_config=_db_config)
    queue_driver.get_connection()
    while True:
        item = _queue.get()
        item.run_and_save(queue_driver)
        _queue.task_done()


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

queue = Queue()
thread = threading.Thread(target=queue_handle, args=(queue, logger, db_mod_name,
                                                     db_cls_name, BaseDbDriver,
                                                     log_config, db_conf),
                          daemon=True)
thread.start()
queue.join()

root = MainForm(driver, log_config, app_config["main_form_conf"], queue)
logger.info('MainForm was started')
root.mainloop()
logger.info('MainForm was closed')
driver.close_connection()
logger.info('DB connection was closed')
