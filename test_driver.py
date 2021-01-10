from sqlite_db_driver import SqliteDbDriver
from datetime import datetime


def test(driver):
    if not driver.is_db_exist():
        driver.init_db()
        print('db created')
    else:
        print('db already exist')

def test_user(driver):
    print('test_user')
    if not driver.chk_conn():
        driver.get_connection()
    print(driver.user_rda())
    name = 'test' + str(datetime.now())
    print(f'name: {name}')

    print('ins')
    driver.user_ins(name)
    res = driver.user_rda()
    print(res)
    id = int(res[-1][0])
    print(id)

    print('upd')
    driver.user_upd(id, name + '_upd')
    print(driver.user_rd(id))

    print('dlt')
    driver.user_dlt(id)
    print(driver.user_rda())

driver = SqliteDbDriver('./db/test_db.db', './db/init_db.sql')
test(driver)
test_user(driver)
driver.close_connection()

