import tkinter as tk
from tkinter import ttk
from core.User import User

class EntryForm(ttk.Frame):
    def __init__(self, root, driver, user):
        super().__init__()
        self.__root = root
        self.__driver = driver
        self.__user = user
        self.__user_dict = self.__read_users()
        self.__cbx_users = None
        self.__create_form()

    def __btn_entry(self):
        self.__user.from_db(self.__user_dict[self.__cbx_users.get()])
        self.__root.destroy()
    
    def __create_form(self):
        self.master.title("Monitoring system")
        lbl_greeting = tk.Label(text="Добро пожаловать\nв систему мониторинга информационных объектов")
        lbl_greeting.grid(row=0, columnspan=2, sticky=tk.W+tk.E)
        lbl_description = tk.Label(text="Для входа в систему выберите пользователя")
        lbl_description.grid(row=1, columnspan=2, sticky=tk.W+tk.E)
        self.__cbx_users = ttk.Combobox(width=20,height=10,values=list(self.__user_dict.keys()),state="readonly")
        self.__cbx_users.grid(row=2, column=0)
        self.__cbx_users.current(0)
        btn_entry = tk.Button(text="Войти в систему", command=self.__btn_entry)
        btn_entry.grid(row=2, column=1)
        self.grid()

    def __read_users(self):
        users_rec = self.__driver.user_rda()
        return {rec[1] : rec[0] for rec in users_rec}
