import base_db_driver
import sqlite3
import os


class SqliteDbDriver(base_db_driver.BaseDbDriver):
    def __init__(self, db_config):
        self._db_file_path = db_config["db_path"]
        self._db_script_path = db_config["init_script_path"]
        self._iso_level = db_config["isolation_level"]
        self._conn = None
        self._cursor = None

    def get_connection(self):
        self._conn = sqlite3.connect(self._db_file_path,
                                     isolation_level=self._iso_level)
        self._cursor = self._conn.cursor()
        return self._cursor is not None

    def is_db_exist(self):
        return os.path.exists(self._db_file_path)

    def init_db(self):
        if not os.path.exists(self._db_file_path):
            if os.path.exists(self._db_script_path):
                with open(self._db_script_path, 'r',
                          encoding='utf-8') as script:
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

    def _table_cnt(self, table_name):
        self._cursor.execute(f"select count(*) from {table_name}")
        return int(self._cursor.fetchone()[0])

    def user_ins(self, user_name):
        """Добавление записи в таблицу user"""
        self._cursor.execute("insert into user(user_name) VALUES(?)",
                             (user_name,))

    def user_upd(self, user_id, user_name):
        """Обновление записи в таблице user"""
        self._cursor.execute("update user set user_name = ? where user_id = ?",
                             (user_name, user_id))

    def user_dlt(self, user_id):
        """Удаление записи из таблицы user"""
        self._cursor.execute("delete from user where user_id = ?",
                             (user_id,))

    def user_rd(self, user_id):
        """Выбрать запись из таблицы user"""
        self._cursor.execute(
            "select user_id, user_name from user where user_id = ?",
            (user_id,))
        return self._cursor.fetchone()

    def user_rda(self):
        """Выбрать все записи из таблицы user"""
        self._cursor.execute("select user_id, user_name from user")
        return self._cursor.fetchall()

    def user_rd_pg(self, limit, offset):
        """Reads a part of records from user table for the pagination

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :return set of records from user table

        """
        self._cursor.execute(
            "select user_id, user_name from user limit ? offset ?",
            (limit, offset))
        return self._cursor.fetchall()

    def user_cnt(self):
        """
        :return count of records from user table
        """
        return self._table_cnt("user")

