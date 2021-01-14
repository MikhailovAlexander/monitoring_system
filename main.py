import tkinter as tk
from form.EntryForm import EntryForm
from sqlite_db_driver import SqliteDbDriver
from core.User import User

root = tk.Tk()
driver = SqliteDbDriver('./db/test_db.db', './db/init_db.sql')
driver.get_connection()
user = User(driver)
app = EntryForm(root, driver, user)
root.mainloop()
print(user.get_name())
