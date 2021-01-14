import tkinter as tk
from forms.EntryForm import EntryForm
from sqlite_db_driver import SqliteDbDriver
from core.User import User

root = tk.Tk()
driver = SqliteDbDriver('./db/test_db.db', './db/init_db.sql')
if not driver.is_db_exist():
    driver.init_db()
driver.get_connection()
user = User(driver)
app = EntryForm(root, driver, user)
root.mainloop()
print(user.get_name())
