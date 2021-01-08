from sqlite_db_driver import SqliteDbDriver


def test(driver):
    if not driver.is_db_exist():
        driver.init_db()
        print('db created')
    else:
        print('db already exist')


driver = SqliteDbDriver('./db/test_db.db', './db/init_db.sql')
test(driver)
