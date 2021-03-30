import logging
import logging.config
import tkinter as tk
from tkinter import ttk, messagebox
import math

from forms.widgets import TableForm, EntryForm, InputForm, Table
from forms.pagination import Pagination
from core.scriptplugin import ScriptPlugin


class MainForm(tk.Tk):
    """Main widget for the program"""

    def __init__(self, driver, log_config, main_form_config):
        self._config = main_form_config
        self._log_config = log_config
        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(__name__)
        self._logger.info('Creating MainForm')
        super().__init__()
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
        self._scr_plug = ScriptPlugin(log_config,
                                      self._config["script_plugin_conf"],
                                      self._driver)
        self._sv_user_name = tk.StringVar()
        self._sv_user_name.trace("w", self._on_upd_sv_user_name)
        self._tb_user = None
        self._pgn_user = None
        self._iv_all_user_scripts = tk.IntVar(value=1)
        self._iv_all_user_scripts.trace("w", self._refresh_tb_script)
        self._tb_script = None
        self._pgn_script = None
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
        self._cbx_users.bind('<<ComboboxSelected>>', self._on_upd_cbx_users)
        self._add_menu_bar()
        nb = ttk.Notebook(self)
        nb.pack(side="bottom", fill="both", expand=True)
        fr_user_tab = self._get_user_tab()
        fr_script_tab = self._get_script_tab()
        f3 = tk.Text(self)
        nb.add(fr_user_tab, text="Пользователи")
        nb.add(fr_script_tab, text="Скрипты")
        nb.add(f3, text='page3')

    def _add_menu_bar(self):
        self._logger.info("Adding menu bar")
        menu = tk.Menu(self)
        new_item = tk.Menu(menu)
        new_item.add_command(label="Новый")
        new_item.add_separator()
        new_item.add_command(label="Выход", command=self._close)
        menu.add_cascade(label="Файл", menu=new_item)
        item = tk.Menu(menu)
        menu.add_cascade(label="Options", menu=item)
        item.add_command(label='Option 1')
        item.add_command(label='Option 2')
        self.config(menu=menu)

    def _on_upd_cbx_users(self, *args):
        user_id = self._user_dict[self._cbx_users.get()]
        if user_id == self._user_id:
            return
        self._user_id = user_id
        self._refresh_tb_script()

    def _get_page_cnt(self, driver_method, row_limit, **kwargs):
        row_cnt = 0
        try:
            row_cnt = driver_method(**kwargs)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения пользователей из БД: {ex}")
        return math.ceil(row_cnt / row_limit)

    def _get_user_tab(self):
        self._logger.info('Creating user tab')
        fr_user_tab = tk.Frame(self)
        fr_controls = tk.Frame(fr_user_tab)
        fr_controls.pack(side="left", fill="y", padx=10)
        fr_user_filters = tk.Frame(fr_controls)
        fr_user_filters.pack(side="top", fill="both", expand=True)
        lbl_user_filters = tk.Label(fr_user_filters, text="Поиск по имени")
        lbl_user_filters.pack(fill="x", expand=True)
        en_user_name = tk.Entry(fr_user_filters,
                                textvariable=self._sv_user_name)
        en_user_name.pack(fill="x", expand=True)
        fr_user_btns = tk.Frame(fr_controls)
        fr_user_btns.pack(side="top", fill="both", expand=True)
        btn_del_user = tk.Button(fr_user_btns, text="Удалить",
                                 command=self._user_del)
        btn_del_user.pack(side="bottom", fill="x", pady=2)
        btn_upd_user = tk.Button(fr_user_btns, text="Редактировать",
                                 command=self._user_upd)
        btn_upd_user.pack(side="bottom", fill="x", pady=2)
        btn_add_user = tk.Button(fr_user_btns, text="Добавить",
                                 command=self._user_add)
        btn_add_user.pack(side="bottom", fill="x", pady=2)
        page_cnt = self._get_page_cnt(self._driver.user_cnt,
                                      self._config["tb_user_row_limit"])
        self._pgn_user = Pagination(fr_controls, 3, page_cnt, prev_button="<<",
                                    next_button=">>",
                                    command=self._load_user_page,
                                    pagination_style=self._config[
                                        "pagination_style"])
        self._pgn_user.pack(side="bottom", fill="both", expand=True)
        self._tb_user = Table(fr_user_tab, headings=('id', 'Имя'))
        self._tb_user.pack(side="right", fill="both", expand=True)
        self._load_user_page(1)
        return fr_user_tab

    def _load_user_page(self, page_num):
        user_name_pattern = None
        value = self._sv_user_name.get()
        if value and value.strip():
            user_name_pattern = value
        offset = (page_num - 1) * self._config["tb_user_row_limit"]
        users_rec = None
        try:
            users_rec = self._driver.user_rd_pg(user_name_pattern,
                                                self._config[
                                                    "tb_user_row_limit"],
                                                offset)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения пользователей из БД: {ex}")
        self._tb_user.clear()
        if users_rec:
            self._tb_user.insert(users_rec)

    def _get_user_index(self):
        index = 0
        for value in self._cbx_users['values']:
            if self._user_dict[value] == self._user_id:
                return index
            index += 1
        self._logger.error(f"Current user (id {self._user_id}) "
                           f"was not found in dictionary")
        raise RuntimeError("Ошибка определения текущего пользователя")

    def _read_users(self):
        try:
            users_rec = self._driver.user_rda()
            return {rec[1]: rec[0] for rec in users_rec}
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения пользователей из БД: {ex}")
            return {}

    def _on_upd_sv_user_name(self, *args):
        value = self._sv_user_name.get()
        if value and value.strip():
            self._refresh_tb_user()

    def _refresh_tb_user(self):
        cur_page = self._pgn_user.current_page
        cur_page_cnt = self._pgn_user.total_pages
        page_cnt = self._get_page_cnt(self._driver.user_cnt,
                                      self._config["tb_user_row_limit"])
        page_cnt = max(1, page_cnt)
        if cur_page_cnt != page_cnt:
            cur_page = min(cur_page, page_cnt)
            self._pgn_user.update(page_cnt, cur_page)
        self._load_user_page(cur_page)

    def _refresh_cbx_users(self):
        self._user_dict = self._read_users()
        self._cbx_users['values'] = list(self._user_dict.keys())
        self._cbx_users.current(self._get_user_index())

    def _user_add(self):
        self._logger.info('User adding is running')
        input_f = InputForm(self._log_config, self,
                            "Ведите имя нового пользователя",
                            btn_entry_txt='Сохранить', btn_exit_txt='Выйти')
        user_name = input_f.get_result()
        if user_name:
            try:
                self._driver.user_ins(user_name)
                self._refresh_tb_user()
                self._refresh_cbx_users()
            except Exception as ex:
                self._logger.exception(ex)
                messagebox.showerror("Data base error",
                                     "Ошибка добавления пользователя в БД: "
                                     f"{ex}")

    def _user_upd(self):
        self._logger.info('User updating is running')
        user_id = self._tb_user.get_selected_id
        user_name_to_edit = self._tb_user.get_selected_value(1)
        if not user_id:
            messagebox.showerror("Application error",
                                 "Пользователь для обновления не выбран")
            return
        input_f = InputForm(self._log_config, self,
                            "Ведите имя пользователя для обнвления",
                            btn_entry_txt='Обновить', btn_exit_txt='Выйти',
                            default_value=user_name_to_edit)
        user_name = input_f.get_result()
        if user_name:
            try:
                self._driver.user_upd(user_id, user_name)
                self._refresh_tb_user()
                self._refresh_cbx_users()
            except Exception as ex:
                self._logger.exception(ex)
                messagebox.showerror("Data base error",
                                     "Ошибка обновления пользователя в БД: "
                                     f"{ex}")

    def _user_del(self):
        self._logger.info('User deleting is running')
        user_id = self._tb_user.get_selected_id
        user_name_to_delete = self._tb_user.get_selected_value(1)
        if not user_id:
            messagebox.showerror("Application error",
                                 "Пользователь для удаления не выбран")
            return
        if user_id == self._user_id:
            messagebox.showerror("Application error",
                                 "Удаление текущего пользоваетеля невозможно")
            return
        if messagebox.askokcancel("Удаление пользователя",
                                  f"Пользователь {user_name_to_delete} "
                                  "будет безвозвратно удален. Продолжить?"):
            try:
                self._driver.user_dlt(user_id)
                self._refresh_tb_user()
                self._refresh_cbx_users()
            except Exception as ex:
                self._logger.exception(ex)
                messagebox.showerror("Data base error",
                                     "Ошибка обновления пользователя в БД: "
                                     f"{ex}")

    def _get_script_tab(self):
        self._logger.info('Creating script tab')
        fr_script_tab = tk.Frame(self)
        fr_script_controls = tk.Frame(fr_script_tab)
        fr_script_controls.pack(side="left", fill="y", padx=10)
        fr_script_filters = tk.Frame(fr_script_controls)
        fr_script_filters.pack(side="top", fill="both", expand=True)
        cb_all_user_scripts = tk.Checkbutton(fr_script_filters,
                                             text="Для всех пользователей",
                                             variable=self._iv_all_user_scripts,
                                             padx=15, pady=10)
        cb_all_user_scripts.pack(fill="x", expand=True)
        # TODO: Add filtres for scripts
        lbl_script_filters = tk.Label(fr_script_filters, text="Поиск по имени")
        lbl_script_filters.pack(fill="x", expand=True)
        en_script_name = tk.Entry(fr_script_filters,
                                textvariable=self._sv_user_name)
        en_script_name.pack(fill="x", expand=True)

        fr_script_btns = tk.Frame(fr_script_controls)
        fr_script_btns.pack(side="top", fill="both", expand=True)
        btn_del_script = tk.Button(fr_script_btns, text="Удалить",
                                   command=self._script_del)
        btn_del_script.pack(side="bottom", fill="x", pady=2)
        btn_upd_script = tk.Button(fr_script_btns, text="Обновить",
                                   command=self._script_upd)
        btn_upd_script.pack(side="bottom", fill="x", pady=2)
        btn_srch_script = tk.Button(fr_script_btns, text="Искать новые",
                                    command=self._script_srch)
        btn_srch_script.pack(side="bottom", fill="x", pady=2)
        # TODO: Add buttons for scripts
        page_cnt = self._get_page_cnt(self._driver.script_cnt,
                                      self._config["tb_script_row_limit"],
                                      user_id=
                                      None if self._iv_all_user_scripts.get()
                                      else self._user_id)
        self._pgn_script = Pagination(fr_script_controls, 3, page_cnt,
                                      prev_button="<<",
                                      next_button=">>",
                                      command=self._load_script_page,
                                      pagination_style=self._config[
                                          "pagination_style"])
        self._pgn_script.pack(side="bottom", fill="both", expand=True)
        self._tb_script = Table(fr_script_tab,
                                headings=("id", "Название", "Описание", "Автор",
                                          "Дата добавления", "Тип объектов",
                                          "Статус"))
        self._tb_script.pack(side="right", fill="both", expand=True)
        self._load_script_page(1)
        return fr_script_tab

    def _load_script_page(self, page_num):
        self._logger.debug("Loading page for tb_script is running, "
                           f"page: {page_num}")
        limit = self._config["tb_script_row_limit"]
        offset = (page_num - 1) * limit
        user_id = None if self._iv_all_user_scripts.get() else self._user_id
        self._logger.debug(f"user_id: {user_id}")
        script_rec = None
        try:
            script_rec = self._scr_plug.get_actual_scripts(limit, offset,
                                                           user_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения скриптов из БД: {ex}")
        self._tb_script.clear()
        if script_rec:
            self._tb_script.insert(script_rec)

    def _refresh_tb_script(self, *args):
        self._logger.debug("Refreshing tb_script is running")
        cur_page = self._pgn_script.current_page
        cur_page_cnt = self._pgn_script.total_pages
        user_id = None if self._iv_all_user_scripts.get() else self._user_id
        page_cnt = self._get_page_cnt(self._driver.script_cnt,
                                      self._config["tb_user_row_limit"],
                                      user_id=user_id)
        page_cnt = max(1, page_cnt)
        if cur_page_cnt != page_cnt:
            self._logger.debug(f"cur_page:{cur_page}; page_cnt:{page_cnt}")
            cur_page = min(cur_page, page_cnt)
            self._pgn_script.update(page_cnt, cur_page)
        self._load_script_page(cur_page)

    def _script_del(self):
        self._logger.info('Script deleting is running')
        script_id = self._tb_script.get_selected_id
        script_name_to_delete = self._tb_script.get_selected_value(1)
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт для удаления не выбран")
            return
        if messagebox.askokcancel("Удаление скрипта",
                                  f"Скрипт {script_name_to_delete} "
                                  "будет безвозвратно удален. Продолжить?"):
            try:
                self._scr_plug.delete_script(script_id)
                self._refresh_tb_script()
            except Exception as ex:
                self._logger.exception(ex)
                messagebox.showerror("Data base error",
                                     "Ошибка удаления скрипта: "
                                     f"{ex}")

    def _script_upd(self):
        self._logger.info('Script updating is running')
        script_id = self._tb_script.get_selected_id
        script_name_to_delete = self._tb_script.get_selected_value(1)
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт для обновления не выбран")
            return
        if messagebox.askokcancel("Обновление скрипта",
                                  f"Скрипт {script_name_to_delete} "
                                  "будет обновлен из файла. Продолжить?"):
            try:
                self._scr_plug.update_script(script_id)
                self._refresh_tb_script()
            except Exception as ex:
                self._logger.exception(ex)
                messagebox.showerror("Data base error",
                                     "Ошибка обновления скрипта: "
                                     f"{ex}")

    def _script_srch(self):
        self._logger.info("Script searching is running")
        new_scripts = None
        try:
            new_scripts = self._scr_plug.search_scripts()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script searching error",
                                 f"Ошибка поиска скриптов: {ex}")
        if not new_scripts:
            messagebox.showinfo("Поиск скриптов", "Новых скриптов не найдено")
            return
        tb_headings = ("Файл", "Название", "Описание", "Автор", "Статус")
        tb_form = TableForm(self._log_config, self, "Выберите скрипт",
                            tb_headings, new_scripts,
                            title="Список скриптов для добавления",
                            btn_entry_txt="Добавить в систему")
        file_name = tb_form.get_result()
        if not file_name:
            return
        try:
            self._scr_plug.save_script(file_name)
            self._refresh_tb_script()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка добавления скрипта: {ex}")

    def _close(self):
        self.destroy()
