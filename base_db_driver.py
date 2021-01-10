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

    def user_ins(self, user_name):
        """Добавление записи в таблицу user"""
        pass
        
    def user_upd(self, user_id, user_name):
        """Обновление записи в таблице user"""
        pass

    def user_dlt(self, user_id, u_name):
        """Удаление записи из таблицы user"""
        pass

    def user_rd(self, user_id):
        """Выбрать запись из таблицы user"""
        pass

    def user_rda(self):
        """Выбрать все записи из таблицы user"""
        pass
