import logging
import logging.config
import tkinter as tk
from tkinter import ttk, messagebox


class TableForm(tk.Toplevel):
    """widget for table showing"""

    def __init__(self, log_config, root, lbl_text, tb_headings, tb_rows, title,
                 btn_entry_txt='OK', btn_exit_txt='Отмена'):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info('Creating TableForm')
        super().__init__(root)
        self.grab_set()
        self._result = None
        self._create_form(lbl_text, title, tb_headings, tb_rows, btn_entry_txt,
                          btn_exit_txt)
        self.attributes("-topmost", True)
        self.bind('<Return>',  self._btn_entry)
        self.bind('<Escape>',  self._btn_exit)

    def _create_form(self, lbl_text, title, tb_headings, tb_rows, btn_entry_txt,
                     btn_exit_txt):
        self.title(title)
        lbl_description = tk.Label(self, text=lbl_text)
        lbl_description.grid(row=0, column=0, columnspan=2, sticky="we")

        self._tb = Table(self, headings=tb_headings)
        self._tb.insert(tb_rows)
        self._tb.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        btn_entry = tk.Button(self, text=btn_entry_txt, command=self._btn_entry)
        btn_entry.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        btn_exit = tk.Button(self, text=btn_exit_txt, command=self._btn_exit)
        btn_exit.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    def _btn_entry(self, event=None):
        self._logger.info('Enter on TableForm')
        value = self._tb.get_selected_value(0)
        if value:
            self._result = value
            self.destroy()
            return
        self._logger.warning('Row is not selected')
        messagebox.showerror("select error", "Ни одна строка не выбрана")

    def _btn_exit(self, event=None):
        self._logger.info('TableForm')
        self._result = None
        self.destroy()

    def get_result(self):
        """Return text, which was inserted in textbox"""
        self._logger.info('Returning result from TableForm')
        self.wait_window()
        return self._result


class InputForm(tk.Toplevel):
    """widget for user text input"""

    def __init__(self, log_config, root, lbl_text, btn_entry_txt='OK',
                 btn_exit_txt='Отмена', default_value=None):
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info('Creating InputForm')
        super().__init__(root)
        self.grab_set()
        self._result = None
        self._create_form(lbl_text, btn_entry_txt, btn_exit_txt, default_value)
        self.attributes("-topmost", True)
        self.bind('<Return>',  self._btn_entry)
        self.bind('<Escape>',  self._btn_exit)

    def _create_form(self, lbl_text, btn_entry_txt, btn_exit_txt,
                     default_value):
        self.title("Ввод данных")
        lbl_description = tk.Label(self, text=lbl_text)
        lbl_description.grid(row=0, column=0, columnspan=2, sticky="we")
        self._entry = tk.Entry(self, width=50)
        if default_value:
            self._entry.insert(0, default_value)
        self._entry.focus_set()
        self._entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        btn_entry = tk.Button(self, text=btn_entry_txt, command=self._btn_entry)
        btn_entry.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        btn_exit = tk.Button(self, text=btn_exit_txt, command=self._btn_exit)
        btn_exit.grid(row=2, column=1, padx=10, pady=10, sticky="e")

    def _btn_entry(self, event=None):
        self._logger.info('Enter on InputForm')
        value = self._entry.get()
        if value and str(value).strip():
            self._result = self._entry.get()
            self.destroy()
            return
        self._logger.warning('Text box is empty')
        messagebox.showerror("input error", "Поле ввода не заполнено")

    def _btn_exit(self, event=None):
        self._logger.info('Exit InputForm')
        self._result = None
        self.destroy()

    def get_result(self):
        """Return text, which was inserted in textbox"""
        self._logger.info('Returning result from InputForm')
        self.wait_window()
        return self._result


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

    def get_selected_value(self, column_idx):
        """
        Returns value from the selected row and the specified column

        :param column_idx: Column index to return the value from
        :return: value from the selected row and the specified column

        """
        if self._table.focus() and column_idx < len(self._table["columns"]):
            return self._table.item(self._table.focus())['values'][column_idx]

    def clear(self):
        """Removes all rows from table"""
        self._table.delete(*self._table.get_children())

    def insert(self, rows):
        """insert new rows in the end of table

        :param rows: list of tuples with values to insert

        """
        for row in rows:
            self._table.insert('', tk.END, values=tuple(row))
