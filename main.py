import logging
import logging.config
import json

from forms.mainform import MainForm
from base_db_driver import BaseDbDriver
from core.dynamicimport import DynamicImport

LOG_CONF_FILE_PATH = './core/logger_conf.json'
APP_CONF_FILE_PATH = './core/app_conf.json'


def load_json(json_file_path):
    """Read data from json-file"""
    with open(json_file_path, 'r') as json_file:
        return json.load(json_file)


def get_logger(log_config):
    """return logger object

    log_config - logger settings dictionary

    """
    logging.config.dictConfig(log_config)
    return logging.getLogger(__name__)


log_config = load_json(LOG_CONF_FILE_PATH)
logger = get_logger(log_config)
logger.info('logger was created')

app_config = load_json(APP_CONF_FILE_PATH)
logger.info('App config was read')
db_conf = app_config["db_conf"]
db_mod_name = db_conf["db_driver_module"]
db_cls_name = db_conf["db_driver_class"]
driver = DynamicImport.get_object(logger, db_mod_name, db_cls_name,
                                  BaseDbDriver, db_config=db_conf)
if not driver.is_db_exist():
    logger.info('DB is not exist')
    driver.init_db()
    logger.info('DB was created')
driver.get_connection()
logger.info('DB connection was opened')
root = MainForm(driver, log_config, app_config["main_form_conf"])
logger.info('MainForm was started')
root.mainloop()
logger.info('MainForm was closed')
driver.close_connection()
logger.info('DB connection was closed')
