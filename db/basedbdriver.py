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

    def user_rd_pg(self, pattern, limit, offset):
        """Reads a part of records from user table for the pagination

        :param pattern - user name part for like search
        :param limit - row count constraint
        :param offset - row count for shifting the results
        :return set of records from user table

        """
        pass

    def user_cnt(self):
        """
        :return count of records from user table
        """
        pass

    def script_rda(self):
        """
        :return all records from user table
        """
        pass

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
        pass

    def script_ins(self, script_name, script_description, script_author,
                   script_beg_date, script_hash, object_type_id):
        """Inserts new script in script table"""
        pass

    def script_rd(self, script_id):
        """Reads a records from script table

        :param script_id - script table record identifier
        :return record from script table

        """
        pass

    def script_upd(self, script_id, script_name, script_description,
                   script_author, script_hash, object_type_id):
        """Updates a records from script table"""
        pass

    def script_del(self, script_id, script_end_date):
        """Set end date value for target record in script table

        :param script_id - script table record identifier
        :param script_end_date - script end date value to set
        :return void
        """
        pass

    def script_all_cnt(self):
        """
        :return count of records from script table
        """
        pass

    def script_cnt(self, user_id):
        """

        :param user_id: identifier from table user for checking availability
        :return count of actual records from script table
        """
        pass

    def user_script_link_srch(self, user_id, script_id):
        """

        :param user_id: user table record identifier for searching link
        :param script_id - script table record identifier for searching link
        :return first actual link record for script and user
        """
        pass

    def user_script_link_ins(self, user_id, script_id,
                             user_script_link_beg_date):
        """Inserts new link in user_script_link table"""
        pass

    def user_script_link_del(self, user_script_link_id,
                             user_script_link_end_date):
        """Set end date value for target record in user_script_link table

        :param user_script_link_id - user_script_link table record identifier
        :param user_script_link_end_date - end date value to set
        :return void
        """
        pass

    def fact_check_rd_pg(self, limit, offset, user_id, script_id,
                         user_name_pattern, script_name_pattern, date_from,
                         date_to):
        """Reads a part of records from fact_check table for the pagination

        :param limit - row count constraint
        :param offset - row count for shifting the results
        :param user_id: identifier from table user for checking availability
        :param script_id - script table record identifier
        :param user_name_pattern: user name part for like search
        :param script_name_pattern: script name part for like search
        :param date_from: begin date constraint fot user_beg_date
        :param date_to: end date constraint fot user_beg_date
        :return set of records from fact_check table

        """
        pass
