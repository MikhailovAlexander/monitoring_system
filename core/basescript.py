from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum


class ObjectType(Enum):
    """Object type enumeration"""
    FILE = 1
    DB_RECORD = 2
    DB_OBJECT = 3


class ErrorLevel(Enum):
    """Error level enumeration"""
    TRIVIAL = 1
    WARNING = 2
    ERROR = 3


class CheckObject(object):
    """Class for script result object"""
    def __init__(self, name, identifier, comment, author, date, error_level,
                 fact_check_id):
        self._name = name
        self._identifier = identifier
        self._comment = comment
        self._author = author
        self._date = date
        self._error_level = error_level
        self._fact_check_id = fact_check_id

    def to_db_row(self):
        """Returns tuple of values to insert in db"""
        return (self._name, self._identifier, self._comment, self._author,
                self._date, self._error_level.value, self._fact_check_id)


class BaseScript(object):
    """Abstract class which defines script object"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def test(self):
        """Checks resources which is used by script

        :return bool value

        """
        pass

    @abstractmethod
    def run(self, fact_check_id):
        """Runs script

        :param fact_check_id - fact_check table record identifier
        :return Count of checked objects and script results (set of records)
        """
        pass

    @abstractproperty
    def name(self):
        """Returns script name"""
        pass

    @abstractproperty
    def description(self):
        """Returns script description"""
        pass

    @abstractproperty
    def author(self):
        """Returns script author"""
        pass

    @abstractproperty
    def object_type(self):
        """Returns script results type"""
        pass
