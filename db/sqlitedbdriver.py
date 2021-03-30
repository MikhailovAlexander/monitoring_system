import logging
import logging.config
import sqlite3
import os

from db.basedbdriver import BaseDbDriver


class SqliteDbDriver(BaseDbDriver):
    def __init__(self, log_config, db_config):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
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

    def user_rd_pg(self, pattern, limit, offset):
        """Reads a part of records from user table for the pagination

        :param pattern - user name part for like search
        :param limit - row count constraint
        :param offset - row count for shifting the results
        :return set of records from user table

        """
        self._cursor.execute(
            "select user_id, user_name from user "
            "where ?1 is null or user_name like '%' || ?1 || '%' "
            "limit ?2 offset ?3",
            (pattern, limit, offset))
        return self._cursor.fetchall()

    def user_cnt(self):
        """
        :return count of records from user table
        """
        return self._table_cnt("user")

    def script_rda(self):
        """
        :return all records from user table
        """
        self._cursor.execute("select script_id, script_name, "
                             "script_description, script_author, "
                             "script_beg_date, script_end_date, script_hash, "
                             "object_type_id from script")
        return self._cursor.fetchall()

    def script_rd_pg(self, limit, offset, user_id, name_pattern, date_from,
                     date_to):
        """Reads a part of records from script table for the pagination

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :param user_id: identifier from table user for checking availability
        :param name_pattern: script name part for like search
        :param date_from: begin date constraint fot user_beg_date
        :param date_to: end date constraint fot user_beg_date
        :return set of records from script table

        """
        self._logger.debug(f"dates: {date_from}; {date_to}")
        self._cursor.execute(
            "select "
            "	s.script_hash,"
            "	s.script_id,"
            "	s.script_name,"
            "	s.script_description,"
            "	s.script_author,"
            "	s.script_beg_date,"
            "	ot.object_type_name "
            "from script as s"
            "	inner join object_type as ot "
            "       on ot.object_type_id = s.object_type_id "
            "where script_end_date is null "
            "	and (?3 is null "
            "		or exists( "
            "			select 1 from user_script_link as usl "
            "			where usl.user_id = ?3 "
            "				and usl.script_id = s.script_id "
            "				and usl.user_script_link_end_date is null))"
            "   and (?4 is null or script_name like '%' || ?4 || '%') "
            "   and (?5 is null or date(script_beg_date) >= ?5) "
            "   and (?6 is null or date(script_beg_date) <= ?6) "
            "limit ?1 offset ?2",
            (limit, offset, user_id, name_pattern, date_from, date_to))
        return self._cursor.fetchall()

    def script_ins(self, script_name, script_description, script_author,
                   script_beg_date, script_hash, object_type_id):
        """Inserts new script in script table"""
        self._cursor.execute("insert into script("
                             "	script_name,"
                             "	script_description,"
                             "	script_author,"
                             "	script_beg_date,"
                             "	script_end_date,"
                             "	script_hash,"
                             "	object_type_id) "
                             "values(?,?,?,?,null,?,?)",
                             (script_name, script_description, script_author,
                              script_beg_date, script_hash, object_type_id))

    def script_rd(self, script_id):
        """Reads a records from script table

        :param script_id - script table record identifier
        :return record from script table

        """
        self._cursor.execute(
            "select "
            "	s.script_id,"
            "	s.script_name,"
            "	s.script_description,"
            "	s.script_author,"
            "	s.script_beg_date,"
            "	s.script_hash,"
            "	s.object_type_id "
            "from script as s "
            "where script_id = ?",
            (script_id, ))
        return self._cursor.fetchone()

    def script_upd(self, script_id, script_name, script_description,
                   script_author, script_hash, object_type_id):
        """Updates a records from script table"""
        self._cursor.execute("update script set"
                             "	script_name = ?2,"
                             "	script_description = ?3,"
                             "	script_author = ?4,"
                             "	script_hash = ?5,"
                             "	object_type_id = ?6 "
                             "where script_id = ?1",
                             (script_id, script_name, script_description,
                              script_author, script_hash, object_type_id))

    def script_del(self, script_id, script_end_date):
        """Set end date value for target record in script table

        :param script_id - script table record identifier
        :param script_end_date - script end date value to set
        :return void
        """
        self._cursor.execute("update script set script_end_date = ?2 "
                             "where script_id = ?1",
                             (script_id, script_end_date))

    def script_all_cnt(self):
        """
        :return count of records from script table
        """
        return self._table_cnt("script")

    def script_cnt(self, user_id):
        """

        :param user_id: identifier from table user for checking availability
        :return count of actual records from script table
        """
        self._cursor.execute(
            "select count(s.script_id) as cnt "
            "from script as s"
            "	inner join object_type as ot "
            "       on ot.object_type_id = s.object_type_id "
            "where script_end_date is null "
            "	and (?1 is null "
            "		or exists( "
            "			select 1 from user_script_link as usl "
            "			where usl.user_id = ?1 "
            "				and usl.script_id = s.script_id "
            "				and usl.user_script_link_end_date is not null))",
            (user_id,))
        return self._cursor.fetchone()[0]

    def user_script_link_srch(self, user_id, script_id):
        """

        :param user_id: user table record identifier for searching link
        :param script_id - script table record identifier for searching link
        :return first actual link record for script and user
        """
        pass
        self._cursor.execute(
            "select "
            "	user_script_link_id,"
            "	user_script_link_beg_date "
            "from user_script_link "
            "where user_script_link_end_date is null "
            "	and user_id = ?1 "
            "	and script_id = ?2 "
            "limit 1",
            (user_id, script_id))
        return self._cursor.fetchone()

    def user_script_link_ins(self, user_id, script_id,
                             user_script_link_beg_date):
        """Inserts new link in user_script_link table"""
        self._cursor.execute(
            "insert into user_script_link("
            "	user_id,"
            "	script_id,"
            "	user_script_link_beg_date) "
            "values(?,?,?)",
            (user_id, script_id, user_script_link_beg_date))

    def user_script_link_del(self, user_script_link_id,
                             user_script_link_end_date):
        """Set end date value for target record in user_script_link table

        :param user_script_link_id - user_script_link table record identifier
        :param user_script_link_end_date - end date value to set
        :return void
        """
        self._logger.debug(f"params: {user_script_link_id}; "
                           f"{user_script_link_end_date}")
        self._cursor.execute(
            "update user_script_link "
            "set user_script_link_end_date = ?2 "
            "where user_script_link_id = ?1",
            (user_script_link_id, user_script_link_end_date))
