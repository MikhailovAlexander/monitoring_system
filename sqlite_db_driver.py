import base_db_driver
import sqlite3
import os


class SqliteDbDriver(base_db_driver.BaseDbDriver):
    def __init__(self, db_file_path, db_script_path):
        self._db_file_path = db_file_path
        self._db_script_path = db_script_path
        self._conn = None
        self._cursor = None

    def get_connection(self):
        self._conn = sqlite3.connect(self._db_file_path, isolation_level=None)
        self._cursor = self._conn.cursor()
        return self._cursor is not None

    def is_db_exist(self):
        return os.path.exists(self._db_file_path)

    def init_db(self):
        if not os.path.exists(self._db_file_path):
            if os.path.exists(self._db_script_path):
                with open(self._db_script_path, 'r', encoding='utf-8') as script:
                    script_text = script.read()
                try:
                    if self.get_connection():
                        self._cursor.executescript(script_text)
                except sqlite3.Error as e:
                    print('Ошибка БД: ' + str(e))  # throw exception
            else:
                print('Не найден скрипт инициализации БД')  # throw exception
        else:
            print('БД уже существует')  # throw exception

    def chk_conn(self):
        """Проверка соединения с БД"""
        if self._conn:
            try:
                self._conn.cursor()
                return True
            except sqlite3.Error:
                return False
        else:
            return False
        
    def close_cursor(self):
        """Метод для закрытия курсора, если он существует"""
        if self._cursor:
            self._cursor.close()

    def close_connection(self):
        """Метод для закрытия соединения. Закрывает кусор и соединение,
           если они существуют"""
        self.close_cursor()
        if self._conn:
            self._conn.close()
