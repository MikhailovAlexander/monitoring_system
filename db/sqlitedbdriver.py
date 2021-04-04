import logging
import logging.config
import sqlite3
import os

from db.basedbdriver import BaseDbDriver


class SqliteDbDriver(BaseDbDriver):
    """A class for enabling the program to interact
    with the sqlite database

    """
    def __init__(self, log_config, db_config):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._db_file_path = db_config["db_path"]
        self._db_script_path = db_config["init_script_path"]
        self._iso_level = db_config["isolation_level"]
        self._conn = None
        self._cursor = None

    def get_connection(self):
        """Opens a database connection and creates a cursor object

        :return bool value: True if the cursor exists

        """
        self._conn = sqlite3.connect(self._db_file_path,
                                     isolation_level=self._iso_level)
        self._cursor = self._conn.cursor()
        return self._cursor is not None

    def is_db_exist(self):
        """Checks database existing

        :return bool value

        """
        return os.path.exists(self._db_file_path)

    def init_db(self):
        """Creates a database and inserts the initial data"""
        if not os.path.exists(self._db_file_path):
            if os.path.exists(self._db_script_path):
                with open(self._db_script_path, 'r',
                          encoding='utf-8') as script:
                    script_text = script.read()
                try:
                    if self.get_connection():
                        self._cursor.executescript(script_text)
                except sqlite3.Error as ex:
                    self._logger.exception(ex)
                    raise RuntimeError("Ошибка выполнения "
                                       f"скрипта инициализации: {ex}")
            else:
                raise RuntimeError("Не найден скрипт инициализации: "
                                   f"{self._db_script_path}")
        else:
            raise RuntimeError("Ошибка инициализации: БД уже существует"
                               f"{self._db_file_path}")

    def chk_conn(self):
        """Checks the database connection

        :return bool value

        """
        if self._conn:
            try:
                self._conn.cursor()
                return True
            except sqlite3.Error:
                return False
        else:
            return False

    def close_cursor(self):
        """Closes the database cursor if it exists"""
        if self._cursor:
            self._cursor.close()

    def close_connection(self):
        """Closes the database cursor and the connection if they exist"""
        self.close_cursor()
        if self._conn:
            self._conn.close()

    def _table_cnt(self, table_name):
        self._cursor.execute(f"select count(*) from {table_name}")
        return int(self._cursor.fetchone()[0])

    def begin_transaction(self):
        """Starts a database transaction"""
        self._cursor.execute("begin transaction;")

    def commit(self):
        """Commits a database transaction"""
        self._cursor.execute("commit;")

    def rollback(self):
        """Rollbacks a database transaction"""
        self._cursor.execute("rollback;")

    def user_ins(self, user_name):
        """Inserts a new record in the user table

        :param user_name value to insert
        :return void

        """
        self._cursor.execute("insert into user(user_name) VALUES(?)",
                             (user_name,))

    def user_upd(self, user_id, user_name):
        """Updates a record in the user table

        :param user_id record identifier in the user table
        :param user_name value to update
        :return void

        """
        self._cursor.execute("update user set user_name = ? where user_id = ?",
                             (user_name, user_id))

    def user_dlt(self, user_id):
        """Deletes a record from the user table

        :param user_id record identifier in the user table
        :return void

        """
        self._cursor.execute("delete from user where user_id = ?",
                             (user_id,))

    def user_rd(self, user_id):
        """Reads a record from the user table

        :param user_id record identifier in the user table
        :return a record from the user table

        """
        self._cursor.execute(
            "select user_id, user_name from user where user_id = ?",
            (user_id,))
        return self._cursor.fetchone()

    def user_rda(self):
        """Reads all records from the user table

        :return set of records from the user table

        """
        self._cursor.execute("select user_id, user_name from user")
        return self._cursor.fetchall()

    def user_rd_pg(self, pattern, limit, offset):
        """Reads a part of records from the user table for the pagination

        :param pattern - user name part for the like search
        :param limit - row count constraint
        :param offset - row count for shifting the results
        :return set of records from the user table

        """
        self._cursor.execute(
            "select "
            "   u.user_id,"
            "   u.user_name,"
            "   count(distinct usl.script_id) as script_cnt, "
            "   count(distinct fc.fact_check_id) as check_cnt "
            "from user as u"
            "   left join user_script_link as usl "
            "       on usl.user_id = u.user_id "
            "       and usl.user_script_link_end_date is null "
            "   left join fact_check as fc "
            "       on fc.user_script_link_id = usl.user_script_link_id "
            ""
            "where ?1 is null or u.user_name like '%' || ?1 || '%' "
            "group by u.user_id, u.user_name "
            "limit ?2 offset ?3",
            (pattern, limit, offset))
        return self._cursor.fetchall()

    def user_cnt(self):
        """
        :return count of records from the user table
        """
        return self._table_cnt("user")

    def script_rda(self):
        """
        :return all records from the script table
        """
        self._cursor.execute("select script_id, script_name, "
                             "script_description, script_author, "
                             "script_beg_date, script_end_date, script_hash, "
                             "object_type_id from script")
        return self._cursor.fetchall()

    def script_rd_pg(self, limit, offset, user_id, name_pattern, date_from,
                     date_to):
        """Reads a part of records from the script table for the pagination

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :param user_id: identifier from the user table for checking availability
        :param name_pattern: script name part for like search
        :param date_from: begin date constraint for user_beg_date
        :param date_to: end date constraint for user_beg_date
        :return set of records from the script table

        """
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
        """Inserts a new script in the script table"""
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
        """Reads record from the script table

        :param script_id identifier from the script table
        :return record from the script table

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
        """Updates record from the script table"""
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
        """Set end date value for the target record in the script table

        :param script_id identifier from the script table
        :param script_end_date script end date value to set
        :return void

        """
        self._cursor.execute("update script set script_end_date = ?2 "
                             "where script_id = ?1",
                             (script_id, script_end_date))

    def script_all_cnt(self):
        """
        :return count of records from the script table

        """
        return self._table_cnt("script")

    def script_cnt(self, user_id):
        """

        :param user_id: identifier from the user table
        :return count of actual records from the script table

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

        :param user_id: identifier from the user table for link searching
        :param script_id - identifier from the script table for  link searching
        :return first actual link record for the script and the user

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
        """Inserts a new link into the user_script_link table"""
        self._cursor.execute(
            "insert into user_script_link("
            "	user_id,"
            "	script_id,"
            "	user_script_link_beg_date) "
            "values(?,?,?)",
            (user_id, script_id, user_script_link_beg_date))

    def user_script_link_del(self, user_script_link_id,
                             user_script_link_end_date):
        """Set end date value for the target record in
        the user_script_link table

        :param user_script_link_id identifier from the user_script_link table
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

    def fact_check_cnt(self, status_id, user_id, script_id, user_name_pattern,
                       script_name_pattern, date_from, date_to):
        """Counts a part of records from the fact_check table for the pagination

        :param status_id: status identifier from the fact_check_status table
        :param user_id: identifier from the user table for checking availability
        :param script_id - script table record identifier
        :param user_name_pattern: user name part for like search
        :param script_name_pattern: script name part for like search
        :param date_from: begin date constraint for user_beg_date
        :param date_to: end date constraint for user_beg_date
        :return count of records from the fact_check table

        """
        self._cursor.execute(
            "select count(fc.fact_check_id) as cnt "
            "from fact_check as fc "
            "	inner join fact_check_status as fcs "
            "		on fcs.fact_check_status_id = fc.fact_check_status_id "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join user as u on u.user_id = usl.user_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "	inner join object_type as ot "
            "       on ot.object_type_id = s.object_type_id "
            "where s.script_end_date is null "
            "	and (?1 is null or ?1 = fcs.fact_check_status_id)"
            "	and (?2 is null or ?2 = u.user_id)"
            "	and (?3 is null or ?3 = s.script_id)"
            "   and (?4 is null or u.user_name like '%' || ?4 || '%') "
            "   and (?5 is null or s.script_name like '%' || ?5 || '%') "
            "   and (?6 is null or date(fc.fact_check_que_date) >= ?6) "
            "   and (?7 is null or date(fc.fact_check_que_date) <= ?7) ",
            (status_id, user_id, script_id, user_name_pattern,
             script_name_pattern, date_from, date_to))
        return self._cursor.fetchone()[0]

    def fact_check_rd(self, fact_check_id):
        """Reads a record from the fact_check table

        :param fact_check_id identifier from the fact_check table
        :return record from the fact_check table

        """
        self._cursor.execute(
            "select "
            "	s.script_name, "
            "	u.user_name, "
            "	ot.object_type_name, "
            "	fc.fact_check_que_date, "
            "	fc.fact_check_end_date, "
            "	fcs.fact_check_status_name, "
            "	fc.fact_check_obj_count, "
            "	(select count(ob.object_id)  "
            "	from object as ob  "
            "	where ob.fact_check_id = fc.fact_check_id) as odj_cnt "
            "from fact_check as fc "
            "	inner join fact_check_status as fcs "
            "		on fcs.fact_check_status_id = fc.fact_check_status_id "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join user as u on u.user_id = usl.user_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "	inner join object_type as ot "
            "       on ot.object_type_id = s.object_type_id "
            "where fc.fact_check_id = ? ", (fact_check_id,))
        return self._cursor.fetchone()

    def fact_check_rd_pg(self, limit, offset, status_id, user_id, script_id,
                         user_name_pattern, script_name_pattern, date_from,
                         date_to):
        """Reads a part of records from the fact_check table for the pagination

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :param status_id: status identifier from the fact_check_status table
        :param user_id: identifier from the table user for checking availability
        :param script_id - script table record identifier
        :param user_name_pattern: user name part for like search
        :param script_name_pattern: script name part for like search
        :param date_from: begin date constraint for user_beg_date
        :param date_to: end date constraint for user_beg_date
        :return set of records from the fact_check table

        """
        self._cursor.execute(
            "select "
            "	fc.fact_check_id, "
            "	s.script_name, "
            "	u.user_name, "
            "	ot.object_type_name, "
            "	fc.fact_check_que_date, "
            "	fc.fact_check_end_date, "
            "	fcs.fact_check_status_name, "
            "	fc.fact_check_obj_count, "
            "	(select count(ob.object_id)  "
            "	from object as ob  "
            "	where ob.fact_check_id = fc.fact_check_id) as odj_cnt "
            "from fact_check as fc "
            "	inner join fact_check_status as fcs "
            "		on fcs.fact_check_status_id = fc.fact_check_status_id "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join user as u on u.user_id = usl.user_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "	inner join object_type as ot "
            "       on ot.object_type_id = s.object_type_id "
            "where s.script_end_date is null "
            "	and (?3 is null or ?3 = fcs.fact_check_status_id)"
            "	and (?4 is null or ?4 = u.user_id)"
            "	and (?5 is null or ?5 = s.script_id)"
            "   and (?6 is null or u.user_name like '%' || ?6 || '%') "
            "   and (?7 is null or s.script_name like '%' || ?7 || '%') "
            "   and (?8 is null or date(fc.fact_check_que_date) >= ?8) "
            "   and (?9 is null or date(fc.fact_check_que_date) <= ?9) "
            "limit ?1 offset ?2",
            (limit, offset, status_id, user_id, script_id, user_name_pattern,
             script_name_pattern, date_from, date_to))
        return self._cursor.fetchall()

    def fact_check_ins(self, fact_check_que_date, user_script_link_id):
        """Inserts a new link into the fact_check table

        :return inserted row identifier

        """
        self._cursor.execute(
            "insert into fact_check("
            "	fact_check_que_date,"
            "	user_script_link_id,"
            "	fact_check_status_id) "
            "values(?,?,1)",
            (fact_check_que_date, user_script_link_id))
        return self._cursor.lastrowid

    def fact_check_que(self):
        """

        :return fact_check and script identifiers with queue status

        """
        self._cursor.execute(
            "select "
            "	fc.fact_check_id, "
            "	s.script_id "
            "from fact_check as fc "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "where fc.fact_check_status_id = 1")
        return self._cursor.fetchall()

    def fact_check_upd(self, fact_check_id, fact_check_end_date,
                       fact_check_obj_count, fact_check_status_id):
        """Updates a record from the fact_check table"""
        self._cursor.execute(
            "update fact_check set"
            "	fact_check_end_date = ?2,"
            "	fact_check_obj_count = ?3,"
            "	fact_check_status_id = ?4 "
            "where fact_check_id = ?1",
            (fact_check_id, fact_check_end_date, fact_check_obj_count,
             fact_check_status_id))

    def fact_check_rd_status(self, fact_check_id):
        """

        :return fact_check_status_id value by record from the fact_check table

        """
        self._cursor.execute(
            "select fc.fact_check_status_id "
            "from fact_check as fc "
            "where fact_check_id = ?",
            (fact_check_id,))
        return self._cursor.fetchone()

    def fact_check_rd_script(self, fact_check_id):
        """

        :return script_id value by record from the fact_check table

        """
        self._cursor.execute(
            "select usl.script_id "
            "from fact_check as fc "
            "    inner join user_script_link as usl "
            "        on usl.user_script_link_id = fc.user_script_link_id "
            "where fact_check_id = ?",
            (fact_check_id,))
        return self._cursor.fetchone()

    def object_ins(self, values):
        """Inserts a set of new records in the object table"""
        self._cursor.executemany(
            "insert into object("
            "	object_name,"
            "	object_identifier,"
            "	object_comment,"
            "	object_author,"
            "	object_date,"
            "	error_level_id,"
            "	fact_check_id) "
            "values(?,?,?,?,?,?,?)", values)

    def object_rd_pg(self, limit, offset, user_id, fact_check_id,
                     error_level_id, object_name_pattern, script_name_pattern,
                     fact_check_end_date_from, fact_check_end_date_to,
                     object_date_from, object_date_to):
        """Reads a part of records from the object table for the pagination

        :param limit: row count constraint
        :param offset: row count for shifting the results
        :param user_id: identifier from the user table
        :param fact_check_id: identifier from the fact_check table
        :param error_level_id: identifier from the error_level table
        :param object_name_pattern: object name part for like search
        :param script_name_pattern: script name part for like search
        :param fact_check_end_date_from: begin date constraint
        for fact_check_end_date
        :param fact_check_end_date_to: end date constraint
        for fact_check_end_date
        :param object_date_from: begin date constraint for object_date
        :param object_date_to: end date constraint for object_date
        :return set of records from the object table

        """
        self._cursor.execute(
            "select "
            "	ob.object_id, "
            "	s.script_name, "
            "	u.user_name, "
            "	fc.fact_check_end_date, "
            "	ob.object_name, "
            "	ob.object_identifier, "
            "	ob.object_comment, "
            "	ob.object_author, "
            "	ob.object_date, "
            "	el.error_level_name "
            "from object as ob "
            "	inner join fact_check as fc "
            "		on fc.fact_check_id = ob.fact_check_id "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join user as u on u.user_id = usl.user_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "	inner join error_level as el "
            "       on el.error_level_id = ob.error_level_id "
            "where s.script_end_date is null "
            "	and (?3 is null or ?3 = u.user_id)"
            "	and (?4 is null or ?4 = ob.fact_check_id)"
            "	and (?5 is null or ?5 = ob.error_level_id)"
            "   and (?6 is null or ob.object_name like '%' || ?6 || '%') "
            "   and (?7 is null or s.script_name like '%' || ?7 || '%') "
            "   and (?8 is null or date(fc.fact_check_end_date) >= ?8) "
            "   and (?9 is null or date(fc.fact_check_end_date) <= ?9) "
            "   and (?10 is null or date(ob.object_date) >= ?10) "
            "   and (?11 is null or date(ob.object_date) <= ?11) "
            "limit ?1 offset ?2",
            (limit, offset, user_id, fact_check_id, error_level_id,
             object_name_pattern, script_name_pattern, fact_check_end_date_from,
             fact_check_end_date_to, object_date_from, object_date_to))
        return self._cursor.fetchall()

    def object_cnt(self, user_id, fact_check_id, error_level_id,
                   object_name_pattern, script_name_pattern,
                   fact_check_end_date_from, fact_check_end_date_to,
                   object_date_from, object_date_to):
        """Counts a part of records from the object table for the pagination

        :param user_id: identifier from the user table
        :param fact_check_id: identifier from the fact_check table
        :param error_level_id: identifier from the error_level table
        :param object_name_pattern: object name part for like search
        :param script_name_pattern: script name part for like search
        :param fact_check_end_date_from: begin date constraint
        for fact_check_end_date
        :param fact_check_end_date_to: end date constraint
        for fact_check_end_date
        :param object_date_from: begin date constraint for object_date
        :param object_date_to: end date constraint for object_date
        :return count of records from the object table

        """
        self._cursor.execute(
            "select count(ob.object_id) as cnt "
            "from object as ob "
            "	inner join fact_check as fc "
            "		on fc.fact_check_id = ob.fact_check_id "
            "	inner join user_script_link as usl "
            "		on usl.user_script_link_id = fc.user_script_link_id "
            "	inner join user as u on u.user_id = usl.user_id "
            "	inner join script as s on s.script_id = usl.script_id "
            "	inner join error_level as el "
            "       on el.error_level_id = ob"
            ".error_level_id "
            "where s.script_end_date is null "
            "	and (?1 is null or ?1 = u.user_id)"
            "	and (?2 is null or ?2 = ob.fact_check_id)"
            "	and (?3 is null or ?3 = ob.error_level_id)"
            "   and (?4 is null or ob.object_name like '%' || ?4 || '%') "
            "   and (?5 is null or s.script_name like '%' || ?5 || '%') "
            "   and (?6 is null or date(fc.fact_check_end_date) >= ?6) "
            "   and (?7 is null or date(fc.fact_check_end_date) <= ?7) "
            "   and (?8 is null or date(ob.object_date) >= ?8) "
            "   and (?9 is null or date(ob.object_date) <= ?9) ",
            (user_id, fact_check_id, error_level_id, object_name_pattern,
             script_name_pattern, fact_check_end_date_from,
             fact_check_end_date_to, object_date_from, object_date_to))
        return self._cursor.fetchone()[0]

    def user_rep(self, date_from, date_to):
        """Query for the user report

        :param date_from: begin date for the report period
        :param date_to: end date for the report period
        :return aggregated data about users for the period

        """
        self._cursor.execute(
            "select "
            "	u.user_id, "
            "	u.user_name, "
            "	count(distinct "
            "		case "
            "			when user_script_link_beg_date <= ?2 "
            "					and (user_script_link_end_date >?2 "
            "					or user_script_link_end_date is null) "
            "				then usl.script_id end) as active_script_cnt, "
            "	count(distinct "
            "		case "
            "			when user_script_link_beg_date >= ?1 "
            "					and user_script_link_beg_date <= ?2 "
            "				then usl.script_id end) as add_script_cnt, "
            "	count(distinct "
            "		case "
            "			when user_script_link_end_date >= ?1 "
            "					and user_script_link_end_date <= ?2 "
            "				then usl.script_id end) as del_script_cnt, "
            "	count(distinct "
            "		case "
            "			when fact_check_que_date >= ?1 "
            "					and fact_check_que_date <= ?2 "
            "				then fc.fact_check_id end) as add_check_cnt, "
            "	count(distinct "
            "		case "
            "			when fact_check_que_date >= ?1 "
            "					and fact_check_que_date <= ?2 "
            "					and fact_check_status_id = 2 "
            "				then fc.fact_check_id end) as ex_check_cnt, "
            "	count(distinct "
            "		case "
            "			when fact_check_que_date >= ?1 "
            "					and fact_check_que_date <= ?2 "
            "					and fact_check_status_id = 3 "
            "				then fc.fact_check_id end) as fl_check_cnt, "
            "	count(distinct "
            "		case "
            "			when fact_check_que_date >= ?1 "
            "					and fact_check_que_date <= ?2 "
            "					and fact_check_status_id = 4 "
            "				then fc.fact_check_id end) as cl_check_cnt "
            "from user as u "
            "	left join user_script_link as usl "
            "		on usl.user_id = u.user_id "
            "	left join fact_check as fc "
            "		on fc.user_script_link_id = usl.user_script_link_id "
            "group by u.user_id, u.user_name",
            (date_from, date_to))
        return self._cursor.fetchall()
