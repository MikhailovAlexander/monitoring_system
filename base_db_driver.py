from abc import ABCMeta, abstractmethod


class BaseDbDriver(metaclass=ABCMeta):

    @abstractmethod
    def is_db_exist(self):
        """Проверка наличия БД"""
        pass

    def init_db(self):
        """Создание БД"""
        pass
    
    def chk_conn(self):
        """Проверка соединения с БД"""
        pass

    def chk_conn(self):
        """Проверка соединения с БД"""
        pass
    
    def close_cursor(self):
        """Метод для закрытия курсора, если он существует"""
        pass
    
    def close_connection(self):
        """Метод для закрытия соединения. Закрывает кусор и соединение,
           если они существуют"""
        pass
    
