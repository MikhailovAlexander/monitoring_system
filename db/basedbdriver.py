from abc import ABCMeta, abstractmethod


class BaseDbDriver(metaclass=ABCMeta):
    """An abstract class for enabling the program to interact
    with the database

    """

    @abstractmethod
    def get_connection(self):
        """Opens a database connection and creates a cursor object

        :return bool value: True if the cursor exists

        """
        pass

    @abstractmethod
    def is_db_exist(self):
        """Checks database existing

        :return bool value

        """
        pass

    @abstractmethod
    def init_db(self):
        """Creates a database and inserts the initial data"""
        pass

    @abstractmethod
    def chk_conn(self):
        """Checks the database connection

        :return bool value

        """
        pass

    @abstractmethod
    def close_cursor(self):
        """Closes the database cursor if it exists"""
        pass

    @abstractmethod
    def close_connection(self):
        """Closes the database cursor and the connection if they exist"""
        pass

    @abstractmethod
    def begin_transaction(self):
        """Starts a database transaction"""
        pass

    @abstractmethod
    def commit(self):
        """Commits a database transaction"""
        pass

    @abstractmethod
    def rollback(self):
        """Rollbacks a database transaction"""
        pass

    @abstractmethod
    def user_ins(self, user_name):
        """Inserts a new record in the user table

        :param user_name value to insert
        :return void
        """
        pass

    @abstractmethod
    def user_upd(self, user_id, user_name):
        """Updates a record in the user table

        :param user_id record identifier in the user table
        :param user_name value to update
        :return void

        """
        pass

    @abstractmethod
    def user_dlt(self, user_id):
        """Deletes a record from the user table

        :param user_id record identifier in the user table
        :return void

        """
        pass

    @abstractmethod
    def user_rd(self, user_id):
        """Reads a record from the user table

        :param user_id record identifier in the user table
        :return a record from the user table

        """
        pass

    @abstractmethod
    def user_rda(self):
        """Reads all records from the user table

        :return set of records from the user table

        """
        pass

    @abstractmethod
    def user_rd_pg(self, pattern, limit, offset):
        """Reads a part of records from the user table for the pagination

        :param pattern - user name part for the like search
        :param limit - row count constraint
        :param offset - row count for shifting the results
        :return set of records from the user table

        """
        pass

    @abstractmethod
    def user_cnt(self):
        """
        :return count of records from the user table
        """
        pass

    @abstractmethod
    def script_rda(self):
        """
        :return all records from the script table
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def script_ins(self, script_name, script_description, script_author,
                   script_beg_date, script_hash, object_type_id):
        """Inserts a new script in the script table"""
        pass

    @abstractmethod
    def script_rd(self, script_id):
        """Reads record from the script table

        :param script_id identifier from the script table
        :return record from the script table

        """
        pass

    @abstractmethod
    def script_upd(self, script_id, script_name, script_description,
                   script_author, script_hash, object_type_id):
        """Updates record from the script table"""
        pass

    @abstractmethod
    def script_del(self, script_id, script_end_date):
        """Set end date value for the target record in the script table

        :param script_id identifier from the script table
        :param script_end_date script end date value to set
        :return void

        """
        pass

    @abstractmethod
    def script_all_cnt(self):
        """
        :return count of records from the script table

        """
        pass

    @abstractmethod
    def script_cnt(self, user_id):
        """

        :param user_id: identifier from the user table
        :return count of actual records from the script table

        """
        pass

    @abstractmethod
    def user_script_link_srch(self, user_id, script_id):
        """

        :param user_id: identifier from the user table for link searching
        :param script_id - identifier from the script table for  link searching
        :return first actual link record for the script and the user

        """
        pass

    @abstractmethod
    def user_script_link_ins(self, user_id, script_id,
                             user_script_link_beg_date):
        """Inserts a new link into the user_script_link table"""
        pass

    @abstractmethod
    def user_script_link_del(self, user_script_link_id,
                             user_script_link_end_date):
        """Set end date value for the target record in
        the user_script_link table

        :param user_script_link_id identifier from the user_script_link table
        :param user_script_link_end_date - end date value to set
        :return void

        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def fact_check_rd(self, fact_check_id):
        """Reads a record from the fact_check table

        :param fact_check_id identifier from the fact_check table
        :return record from the fact_check table

        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def fact_check_ins(self, fact_check_que_date, user_script_link_id):
        """Inserts a new link into the fact_check table

        :return inserted row identifier

        """
        pass

    @abstractmethod
    def fact_check_que(self):
        """

        :return fact_check and script identifiers with queue status

        """
        pass

    @abstractmethod
    def fact_check_upd(self, fact_check_id, fact_check_end_date,
                       fact_check_obj_count, fact_check_status_id):
        """Updates a record from the fact_check table"""
        pass

    @abstractmethod
    def fact_check_rd_status(self, fact_check_id):
        """

        :return fact_check_status_id value by record from the fact_check table

        """
        pass

    @abstractmethod
    def fact_check_rd_script(self, fact_check_id):
        """

        :return script_id value by record from the fact_check table

        """
        pass

    @abstractmethod
    def object_ins(self, values):
        """Inserts a set of new records in the object table"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
