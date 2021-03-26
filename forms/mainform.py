import logging
import logging.config
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class EntryForm(tk.Toplevel):
    """widget for user selection during program launch"""

    def __init__(self, root, user_dict):
        super().__init__(root)
        self.grab_set()
        self._user_dict = user_dict
        self._cbx_users = None
        self._create_form()
        self._user_id = -1
        self.bind('<Return>',  self._btn_entry)
        self.bind('<Escape>',  self._btn_exit)

    def _create_form(self):
        self.title("Monitoring system")
        lbl_greeting = tk.Label(self, text="Добро пожаловать\nв систему "
                                           "мониторинга информационных "
                                           "объектов")
        lbl_greeting.grid(row=0, column=0, columnspan=2, sticky="we")
        lbl_description = tk.Label(self, padx=10, text="Для входа в систему\n"
                                                       "выберите пользователя:")
        lbl_description.grid(row=1, column=0, sticky="we")
        self._cbx_users = ttk.Combobox(self, width=50, height=10,
                                       values=list(self._user_dict.keys()),
                                       state="readonly")
        self._cbx_users.focus_set()
        self._cbx_users.grid(row=1, column=1, padx=10, pady=10)
        self._cbx_users.current(0)
        btn_entry = tk.Button(self, text="Войти в систему",
                              command=self._btn_entry)
        btn_entry.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        btn_exit = tk.Button(self, text="Выйти",
                             command=self._btn_exit)
        btn_exit.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    def _btn_entry(self, event=None):
        self._user_id = self._user_dict[self._cbx_users.get()]
        self.destroy()

    def _btn_exit(self, event=None):
        self._user_id = -1
        self.destroy()

    def get_user_id(self):
        """Return id of the user which was selected in combobox"""
        self.wait_window()
        return self._user_id


class Table(tk.Frame):
    def __init__(self, parent=None, headings=tuple(), rows=tuple()):
        super().__init__(parent)
        self._selectItem = None

        self._table = ttk.Treeview(self, show="headings", selectmode="browse")
        self._table["columns"] = headings
        self._table["displaycolumns"] = headings

        for head in headings:
            self._table.heading(head, text=head, anchor=tk.CENTER)
            self._table.column(head, anchor=tk.CENTER)

        for row in rows:
            self._table.insert('', tk.END, values=tuple(row))

        scroll = tk.Scrollbar(self, command=self._table.yview)
        self._table.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._table.pack(expand=tk.YES, fill=tk.BOTH, anchor="nw")

    @property
    def get_selected_id(self):
        if self._table.focus():
            return self._table.item(self._table.focus())['values'][0]


class MainForm(tk.Tk):
    """Main widget for the program"""

    def __init__(self, driver, log_config):
        super().__init__()
        self._logger_conf = log_config
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info('Creating MainForm')
        self.attributes('-alpha', 0.0)  # make window transparent
        self._driver = driver
        self._user_id = None
        self._user_dict = self._read_users()
        self._cbx_users = None
        self._run_entry_form()
        if self._user_id == -1:  # if the user was not selected
            self.destroy()
            return
        self.after(0, self.attributes, "-alpha", 1.0)  # back to normal
        self.attributes("-topmost", True)
        self._create_form()

    def _run_entry_form(self):
        self._logger.info('Running EntryForm')
        ef = EntryForm(self, self._user_dict)
        self._user_id = ef.get_user_id()

    def _create_form(self):
        self._logger.info('Adding widgets')
        self.title("Monitoring system")
        fr_cur_user = tk.Frame(self)
        fr_cur_user.pack(side="top", fill=tk.Y)
        lbl_cur_users = tk.Label(fr_cur_user, text="Текущий пользователь ")
        lbl_cur_users.pack(side="left", fill="x", expand=True)
        self._cbx_users = ttk.Combobox(fr_cur_user, width=50, height=10,
                                       values=list(self._user_dict.keys()),
                                       state="readonly")
        self._cbx_users.pack(side="left", fill="x", expand=True)
        self._cbx_users.current(self._get_user_index())
        self._add_menu_bar()
        nb = ttk.Notebook(self)
        nb.pack(side="bottom", fill="both", expand=True)
        fr_user_tab = self._get_user_tab()
        f2 = tk.Text(self)
        f3 = tk.Text(self)
        nb.add(fr_user_tab, text='Пользователи')
        nb.add(f2, text='page2')
        nb.add(f3, text='page3')

    def _get_user_tab(self):
        self._logger.info('Creating user tab')
        users_rec = self._driver.user_rda()
        fr_user_tab = tk.Frame(self)
        fr_controls = tk.Frame(fr_user_tab)
        fr_controls.pack(side="left", fill="y", padx=10)
        fr_user_filters = tk.Frame(fr_controls)
        fr_user_filters.pack(side="top", fill="both", expand=True)
        lbl_user_filters = tk.Label(fr_user_filters, text="Фильтры")
        lbl_user_filters.pack(fill="x", expand=True)
        fr_user_btns = tk.Frame(fr_controls)
        fr_user_btns.pack(side="top", fill="both", expand=True)
        lbl_user_btns = tk.Label(fr_user_btns, text="Кнопки")
        lbl_user_btns.pack(fill="x", expand=True)
        btn_add_user = tk.Button(fr_user_btns, text="Добавить",
                                 command=self._user_add)
        btn_add_user.pack(side="top", fill="x", pady=2)
        btn_upd_user = tk.Button(fr_user_btns, text="Редактировать",
                                 command=self._user_upd)
        btn_upd_user.pack(side="top", fill="x", pady=2)
        btn_del_user = tk.Button(fr_user_btns, text="Удалить",
                                 command=self._user_del)
        btn_del_user.pack(side="top", fill="x", pady=2)
        fr_user_pg = tk.Frame(fr_controls)
        fr_user_pg.pack(side="top", fill="both", expand=True)
        lbl_user_pg = tk.Label(fr_user_pg, text="Пэйджинг")
        lbl_user_pg.pack(fill="x", expand=True)
        self._tb_user = Table(fr_user_tab, headings=('id', 'Имя'),
                              rows=users_rec)
        self._tb_user.pack(side="right", fill="both", expand=True)
        return fr_user_tab

    def _get_user_index(self):
        index = 0
        for value in self._cbx_users['values']:
            if self._user_dict[value] == self._user_id:
                return index
            index += 1
        self._logger.error(f"Current user (id {self._user_id}) "
                           f"was not found in dictionary")
        raise RuntimeError("Ошибка определения текущего пользователя")

    def _add_menu_bar(self):
        self._logger.info('Adding menu bar')
        menu = tk.Menu(self)
        new_item = tk.Menu(menu)
        new_item.add_command(label='Новый')
        new_item.add_separator()
        new_item.add_command(label='Выход', command=self._close)
        menu.add_cascade(label='Файл', menu=new_item)
        item = tk.Menu(menu)
        menu.add_cascade(label='Options', menu=item)
        item.add_command(label='Option 1')
        item.add_command(label='Option 2')
        self.config(menu=menu)

    def _read_users(self):
        try:
            users_rec = self._driver.user_rda()
            return {rec[1]: rec[0] for rec in users_rec}
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения пользователей из БД: {ex}")
            return {}

    def _user_add(self):
        pass

    def _user_upd(self):
        print(self._tb_user.get_selected_id)

    def _user_del(self):
        pass

    def _close(self):
        self.destroy()
