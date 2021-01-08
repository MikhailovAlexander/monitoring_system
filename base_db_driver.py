from abc import ABCMeta, abstractmethod


class BaseDbDriver(metaclass=ABCMeta):

    @abstractmethod
    def is_db_exist(self):
        """Проверка наличия БД"""
        pass

    def init_db(self):
        """Создание БД"""
        pass
