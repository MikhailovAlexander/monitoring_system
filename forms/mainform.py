import logging
import logging.config
import tkinter as tk
from tkinter import ttk, messagebox
import math
import datetime

from forms.widgets import DateEntry, TableForm, EntryForm, InputForm, Table
from forms.pagination import Pagination
from core.scriptplugin import ScriptPlugin
from core.scriptqueue import ScriptQueue


class MainForm(tk.Tk):
    """Main widget for the program"""

    def __init__(self, driver, log_config, main_form_config, queue):
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
                                      driver)
        self._scr_queue = ScriptQueue(driver, log_config, self._scr_plug,
                                      queue)

        self._tab = None
        self.sv_current_check_name = tk.StringVar(value="NO SCRIPT")
        self.iv_current_check_id = tk.IntVar()
        self._sv_user_name = tk.StringVar()
        self._sv_user_name.trace("w", self._on_upd_sv_user_name)
        self._tb_user = None
        self._pgn_user = None
        self._iv_showed_script_id = tk.IntVar()
        self._iv_showed_script_id.trace("w", self._on_upd_iv_showed_script_id)
        self._iv_all_user_scripts = tk.IntVar(value=1)
        self._iv_all_user_scripts.trace("w", self._refresh_tb_script)
        self._sv_script_name = tk.StringVar()
        self._sv_script_name.trace("w", self._on_upd_sv_script_name)
        self._iv_period_scripts = tk.IntVar(value=0)
        self._iv_period_scripts.trace("w", self._on_upd_iv_period_scripts)
        self._ed_script_date_from = None
        self._ed_script_date_to = None
        self._tb_script = None
        self._pgn_script = None

        self._lbl_check_context = None
        self._iv_showed_check_id = tk.IntVar()
        self._iv_showed_check_id.trace("w", self._on_upd_iv_showed_check_id)
        self._iv_all_user_checks = tk.IntVar(value=1)
        self._iv_all_user_checks.trace("w", self._refresh_tb_check)
        self._iv_all_script_checks = tk.IntVar(value=1)
        self._iv_all_script_checks.trace("w", self._refresh_tb_check)
        self._iv_status_checks = tk.IntVar(value=-1)
        self._iv_status_checks.trace("w", self._refresh_tb_check)
        self._sv_check_script_name = tk.StringVar()
        self._sv_check_script_name.trace("w", self._refresh_tb_check)
        self._sv_check_user_name = tk.StringVar()
        self._sv_check_user_name.trace("w", self._refresh_tb_check)
        self._iv_period_checks = tk.IntVar(value=0)
        self._iv_period_checks.trace("w", self._on_upd_iv_period_checks)
        self._ed_check_date_from = None
        self._ed_check_date_to = None
        self._tb_check = None
        self._pgn_check = None

        self._lbl_object_context = None
        self._iv_all_user_obj = tk.IntVar(value=1)
        self._iv_all_user_obj.trace("w", self._refresh_tb_obj)
        self._iv_all_check_obj = tk.IntVar(value=1)
        self._iv_all_check_obj.trace("w", self._refresh_tb_obj)
        self._iv_status_obj = tk.IntVar(value=-1)
        self._iv_status_obj.trace("w", self._refresh_tb_obj)
        self._sv_obj_script_name = tk.StringVar()
        self._sv_obj_script_name.trace("w", self._refresh_tb_obj)
        self._sv_obj_name = tk.StringVar()
        self._sv_obj_name.trace("w", self._refresh_tb_obj)
        self._iv_period_checks_obj = tk.IntVar(value=0)
        self._iv_period_checks_obj.trace("w", self._on_upd_iv_period_checks_obj)
        self._ed_check_obj_date_from = None
        self._ed_check_obj_date_to = None
        self._iv_period_obj = tk.IntVar(value=0)
        self._iv_period_obj.trace("w", self._on_upd_iv_period_obj)
        self._pgn_obj = None
        self._tb_obj = None

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
        lbl_cur_users.pack(side="left")
        self._cbx_users = ttk.Combobox(fr_cur_user, width=50, height=10,
                                       values=list(self._user_dict.keys()),
                                       state="readonly")
        self._cbx_users.pack(side="left")
        self._cbx_users.current(self._get_user_index())
        self._cbx_users.bind('<<ComboboxSelected>>', self._on_upd_cbx_users)
        lbl_cur_check = tk.Label(fr_cur_user,
                                 textvariable=self.sv_current_check_name)
        lbl_cur_check.pack(side="right", padx=30)
        self._add_menu_bar()
        self._tab = ttk.Notebook(self)
        self._tab.pack(side="bottom", fill="both", expand=True)
        fr_user_tab = self._get_user_tab()
        fr_script_tab = self._get_script_tab()
        fr_check_tab = self._get_check_tab()
        fr_obj_tab = self._get_object_tab()
        self._tab.add(fr_user_tab, text="Пользователи")
        self._tab.add(fr_script_tab, text="Скрипты")
        self._tab.add(fr_check_tab, text="Проверки")
        self._tab.add(fr_obj_tab, text="Объекты")

    def _add_menu_bar(self):
        self._logger.info("Adding menu bar")
        menu = tk.Menu(self)
        new_item = tk.Menu(menu)
        new_item.add_command(label="Новый")
        new_item.add_separator()
        new_item.add_command(label="Выход", command=self._close)
        menu.add_cascade(label="Файл", menu=new_item)
        item = tk.Menu(menu)
        menu.add_cascade(label="Очередь проверок", menu=item)
        item.add_command(label="Очистить очередь", command=self._queue_clean)
        item.add_command(label="Очистить очередь и отменить проверки",
                         command=self._queue_clean_and_cancel)
        item.add_command(label="Очистить очередь и заполнить из бд",
                         command=self._queue_refresh_from_db)
        self.config(menu=menu)

    def _close(self):
        self.destroy()

    def _queue_clean(self):
        try:
            self._scr_queue.clean()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script queue error",
                                 f"Ошибка очистки очереди проверок: {ex}")

    def _queue_clean_and_cancel(self):
        try:
            self._scr_queue.clean_and_cancel()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script queue error",
                                 f"Ошибка очистки очереди проверок: {ex}")

    def _queue_refresh_from_db(self):
        try:
            self._scr_queue.refresh_from_db(self.iv_current_check_id.get())
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script queue error",
                                 f"Ошибка обновления очереди проверок: {ex}")

    def _on_upd_cbx_users(self, *args):
        user_id = self._user_dict[self._cbx_users.get()]
        if user_id == self._user_id:
            return
        self._user_id = user_id
        self._refresh_tb_script()
        self._refresh_tb_check()

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
        lbl_script_filters = tk.Label(fr_script_filters,
                                      text="Поиск по названию")
        lbl_script_filters.pack(fill="x", expand=True)
        en_script_name = tk.Entry(fr_script_filters,
                                  textvariable=self._sv_script_name)
        en_script_name.pack(fill="x", expand=True)
        cb_period_scripts = tk.Checkbutton(fr_script_filters,
                                           text="Добавленные за период",
                                           variable=self._iv_period_scripts,
                                           padx=15, pady=10)
        cb_period_scripts.pack(fill="x", expand=True)
        self._ed_script_date_from = DateEntry(fr_script_filters,
                                              self._log_config,
                                              "с  ",
                                              command=self._refresh_tb_script)
        self._ed_script_date_from.pack(fill="x", expand=True)
        self._ed_script_date_from.disable()
        self._ed_script_date_to = DateEntry(fr_script_filters,
                                            self._log_config,
                                            "по ",
                                            command=self._refresh_tb_script)
        self._ed_script_date_to.pack(fill="x", expand=True)
        self._ed_script_date_to.disable()
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
        btn_rm_script_to_user = tk.Button(fr_script_btns,
                                          text="Снять видимость для"
                                               "\nтекущего пользователя",
                                          command=self._script_rm_to_user)
        btn_rm_script_to_user.pack(side="bottom", fill="x", pady=2)
        btn_add_script_to_user = tk.Button(fr_script_btns,
                                           text="Добавить видимость для"
                                                "\nтекущего пользователя",
                                           command=self._script_add_to_user)
        btn_add_script_to_user.pack(side="bottom", fill="x", pady=2)
        btn_run_script = tk.Button(fr_script_btns, text="Запустить скрипт",
                                   command=self._on_clk_btn_run_script)
        btn_run_script.pack(side="bottom", fill="x", pady=2)
        btn_show_checks = tk.Button(fr_script_btns, text="Показать проверки",
                                    command=self._on_clk_btn_show_checks)
        btn_show_checks.pack(side="bottom", fill="x", pady=2)
        page_cnt = self._get_page_cnt(self._driver.script_cnt,
                                      self._config["tb_script_row_limit"],
                                      user_id=
                                      None if self._iv_all_user_scripts.get()
                                      else self._user_id)
        self._pgn_script = Pagination(fr_script_controls, 3, page_cnt,
                                      prev_button="<<",
                                      next_button=">>",
                                      command=self._load_script_page,
                                      pagination_style=
                                      self._config["pagination_style"])
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
        name_pattern = None
        value = self._sv_script_name.get()
        if value and value.strip():
            name_pattern = value
        date_from = self._ed_script_date_from.get()
        date_to = self._ed_script_date_to.get()
        script_rec = None
        try:
            script_rec = self._scr_plug.get_actual_scripts(limit, offset,
                                                           user_id,
                                                           name_pattern,
                                                           date_from,
                                                           date_to)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения скриптов из БД: {ex}")
        self._tb_script.clear()
        if script_rec:
            self._tb_script.insert(script_rec)

    def _on_upd_sv_script_name(self, *args):
        value = self._sv_script_name.get()
        if value and value.strip():
            self._refresh_tb_script()

    def _on_upd_iv_period_scripts(self, *args):
        if self._iv_period_scripts.get():
            self._ed_script_date_from.enable()
            self._ed_script_date_to.enable()
        else:
            self._ed_script_date_from.disable()
            self._ed_script_date_to.disable()
        self._refresh_tb_script()

    def _on_clk_btn_run_script(self, *args):
        script_id = self._tb_script.get_selected_id
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт для запуска не выбран")
            return
        link = None
        try:
            link = self._driver.user_script_link_srch(self._user_id, script_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка проверки видимости скрипта: {ex}")
        if not link:
            messagebox.showerror("Application error",
                                 "Скрипт не доступен текущему пользователю")
            return
        try:
            self._scr_queue.put(script_id, link[0])
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script queue error",
                                 f"Ошибка добавления скрипта в очередь: {ex}")

    def _on_clk_btn_show_checks(self, *args):
        script_id = self._tb_script.get_selected_id
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт не выбран")
            return
        self._iv_showed_script_id.set(script_id)
        self._reset_tb_check_params()
        self._tab.select(2)

    def _on_upd_iv_showed_script_id(self, *args):
        script_id = self._iv_showed_script_id.get()
        if not script_id:
            return
        script_rec = None
        try:
            script_rec = self._driver.script_rd(script_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка поиска скрипта: {ex}")
        if script_rec:
            self._lbl_check_context.config(text="Выбранный скрипт: "
                                                f"{script_rec[1]}")
        else:
            self._lbl_check_context.config(text="Выбранный скрипт: не задан")

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

    def _script_add_to_user(self):
        self._logger.info("User script link adding is running")
        script_id = self._tb_script.get_selected_id
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт для добавления не выбран")
            return
        link = None
        try:
            link = self._driver.user_script_link_srch(self._user_id, script_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка проверки видимости скрипта: {ex}")
        if link:
            messagebox.showerror("Application error",
                                 "Скрипт уже доступен текущему пользователю")
            return
        try:
            self._driver.user_script_link_ins(self._user_id, script_id,
                                              datetime.datetime.now())
            self._refresh_tb_script()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка добавления видимости скрипта: {ex}")

    def _script_rm_to_user(self):
        self._logger.info("User script link removing is running")
        script_id = self._tb_script.get_selected_id
        if not script_id:
            messagebox.showerror("Application error",
                                 "Скрипт для снятия видимости не выбран")
            return
        link = None
        try:
            link = self._driver.user_script_link_srch(self._user_id, script_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка проверки видимости скрипта: {ex}")
        if not link:
            messagebox.showerror("Application error",
                                 "Скрипт не доступен текущему пользователю")
            return
        try:
            self._driver.user_script_link_del(link[0], datetime.datetime.now())
            self._refresh_tb_script()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка снятия видимости скрипта: {ex}")

    def _get_check_tab(self):
        self._logger.info('Creating check tab')
        fr_check_tab = tk.Frame(self)
        fr_check_controls = tk.Frame(fr_check_tab)
        fr_check_controls.pack(side="left", fill="y", padx=10)
        self._lbl_check_context = tk.Label(fr_check_controls,
                                           text="Выбранный скрипт: не задан")
        self._lbl_check_context.pack(fill="x", expand=True)
        fr_check_filters = tk.Frame(fr_check_controls)
        fr_check_filters.pack(side="top", fill="both", expand=True)
        cb_all_user_checks = tk.Checkbutton(fr_check_filters,
                                            text="Для всех пользователей",
                                            variable=self._iv_all_user_checks,
                                            padx=15)
        cb_all_user_checks.pack(fill="x", expand=True)
        cb_all_script_checks = tk.Checkbutton(fr_check_filters,
                                              text="Для всех скриптов",
                                              variable=
                                              self._iv_all_script_checks,
                                              padx=15)
        cb_all_script_checks.pack(fill="x", expand=True)
        rb_all_status_checks = tk.Radiobutton(fr_check_filters,
                                              text="Любой статус", value=-1,
                                              variable=self._iv_status_checks,
                                              padx=15)
        rb_all_status_checks.pack(fill="x", expand=True)
        rb_qu_status_checks = tk.Radiobutton(fr_check_filters,
                                             text="В очереди", value=1,
                                             variable=self._iv_status_checks,
                                             padx=15)
        rb_qu_status_checks.pack(fill="x", expand=True)
        rb_ex_status_checks = tk.Radiobutton(fr_check_filters,
                                             text="Выполненные", value=2,
                                             variable=self._iv_status_checks,
                                             padx=15)
        rb_ex_status_checks.pack(fill="x", expand=True)
        rb_fl_status_checks = tk.Radiobutton(fr_check_filters,
                                             text="Завершенные с ошибкой",
                                             value=3,
                                             variable=self._iv_status_checks,
                                             padx=15)
        rb_fl_status_checks.pack(fill="x", expand=True)
        rb_cl_status_checks = tk.Radiobutton(fr_check_filters,
                                             text="Отмененные",
                                             value=4,
                                             variable=self._iv_status_checks,
                                             padx=15)
        rb_cl_status_checks.pack(fill="x", expand=True)
        lbl_script_filter = tk.Label(fr_check_filters,
                                     text="Поиск по названию скрипта")
        lbl_script_filter.pack(fill="x", expand=True)
        en_check_script_name = tk.Entry(fr_check_filters,
                                        textvariable=self._sv_check_script_name)
        en_check_script_name.pack(fill="x", expand=True)
        lbl_user_filter = tk.Label(fr_check_filters,
                                   text="Поиск по пользователю")
        lbl_user_filter.pack(fill="x", expand=True)
        en_check_user_name = tk.Entry(fr_check_filters,
                                      textvariable=self._sv_check_user_name)
        en_check_user_name.pack(fill="x", expand=True)
        cb_period_checks = tk.Checkbutton(fr_check_filters,
                                          text="Проведенные за период",
                                          variable=self._iv_period_checks,
                                          padx=15, pady=10)
        cb_period_checks.pack(fill="x", expand=True)
        self._ed_check_date_from = DateEntry(fr_check_filters,
                                             self._log_config,
                                             "с  ",
                                             command=self._refresh_tb_check)
        self._ed_check_date_from.pack(fill="x", expand=True)
        self._ed_check_date_from.disable()
        self._ed_check_date_to = DateEntry(fr_check_filters,
                                           self._log_config,
                                           "по ",
                                           command=self._refresh_tb_check)
        self._ed_check_date_to.pack(fill="x", expand=True)
        self._ed_check_date_to.disable()
        fr_check_btns = tk.Frame(fr_check_controls)
        fr_check_btns.pack(side="top", fill="both", expand=True)
        btn_cancel_check = tk.Button(fr_check_btns, text="Отменить проверку",
                                     command=self._check_cancel)
        btn_cancel_check.pack(side="bottom", fill="x", pady=2)
        btn_rerun_check = tk.Button(fr_check_btns, text="Запустить повторно",
                                    command=self._rerun_check)
        btn_rerun_check.pack(side="bottom", fill="x", pady=2)
        btn_show_obj = tk.Button(fr_check_btns, text="Просмотреть объекты",
                                 command=self._show_obj)
        btn_show_obj.pack(side="bottom", fill="x", pady=2)
        page_cnt = self._get_page_cnt(self._driver.fact_check_cnt,
                                      self._config["tb_check_row_limit"],
                                      status_id=None, user_id=None,
                                      script_id=None,
                                      user_name_pattern=None,
                                      script_name_pattern=None,
                                      date_from=None, date_to=None)
        self._pgn_check = Pagination(fr_check_controls, 3, page_cnt,
                                     prev_button="<<",
                                     next_button=">>",
                                     command=self._load_check_page,
                                     pagination_style=self._config[
                                         "pagination_style"])
        self._pgn_check.pack(side="bottom", fill="both", expand=True)
        self._tb_check = Table(fr_check_tab,
                               headings=("id", "Название скрипта",
                                         "Пользователь", "Тип объекта",
                                         "Дата постановки в очередь",
                                         "Дата выполнения", "Статус",
                                         "Проверено объектов",
                                         "Выявлено объектов"))
        self._tb_check.pack(side="right", fill="both", expand=True)
        self._load_check_page(1)
        return fr_check_tab

    def _load_check_page(self, page_num):
        self._logger.debug("Loading page for tb_check is running, "
                           f"page: {page_num}")
        limit = self._config["tb_script_row_limit"]
        offset = (page_num - 1) * limit
        user_id = None if self._iv_all_user_checks.get() else self._user_id
        script_id = None if self._iv_all_script_checks.get()\
            else self._iv_showed_script_id.get()
        status_id = self._iv_status_checks.get()
        status_id = None if status_id == -1 else status_id
        self._logger.debug(f"status_id: {status_id}")
        script_name_pattern = None
        value = self._sv_check_script_name.get()
        if value and value.strip():
            script_name_pattern = value
        user_name_pattern = None
        value = self._sv_check_user_name.get()
        if value and value.strip():
            user_name_pattern = value
        date_from = self._ed_check_date_from.get()
        date_to = self._ed_check_date_to.get()
        check_rec = None
        try:
            check_rec = self._driver.fact_check_rd_pg(limit, offset,
                                                      status_id=status_id,
                                                      user_id=user_id,
                                                      script_id=script_id,
                                                      user_name_pattern=
                                                      user_name_pattern,
                                                      script_name_pattern=
                                                      script_name_pattern,
                                                      date_from=date_from,
                                                      date_to=date_to)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения проверок из БД: {ex}")
        self._tb_check.clear()
        if check_rec:
            self._tb_check.insert(check_rec)

    def _refresh_tb_check(self, *args):
        self._logger.debug("Refreshing tb_check is running")
        cur_page = self._pgn_check.current_page
        cur_page_cnt = self._pgn_check.total_pages
        user_id = None if self._iv_all_user_checks.get() else self._user_id
        script_id = None if self._iv_all_script_checks.get()\
            else self._iv_showed_script_id.get()
        status_id = self._iv_status_checks.get()
        status_id = None if status_id == -1 else status_id
        script_name_pattern = None
        value = self._sv_check_script_name.get()
        if value and value.strip():
            script_name_pattern = value
        user_name_pattern = None
        value = self._sv_check_user_name.get()
        if value and value.strip():
            user_name_pattern = value
        date_from = self._ed_check_date_from.get()
        date_to = self._ed_check_date_to.get()
        page_cnt = self._get_page_cnt(self._driver.fact_check_cnt,
                                      self._config["tb_user_row_limit"],
                                      status_id=status_id,
                                      user_id=user_id,
                                      script_id=script_id,
                                      user_name_pattern=user_name_pattern,
                                      script_name_pattern=script_name_pattern,
                                      date_from=date_from,
                                      date_to=date_to)
        page_cnt = max(1, page_cnt)
        if cur_page_cnt != page_cnt:
            self._logger.debug(f"cur_page:{cur_page}; page_cnt:{page_cnt}")
            cur_page = min(cur_page, page_cnt)
            self._pgn_check.update(page_cnt, cur_page)
        self._load_check_page(cur_page)

    def _reset_tb_check_params(self):
        self._iv_all_user_checks.set(1)
        self._iv_all_script_checks.set(0)
        self._iv_status_checks.set(-1)

    def _on_upd_iv_period_checks(self, *args):
        if self._iv_period_checks.get():
            self._ed_check_date_from.enable()
            self._ed_check_date_to.enable()
        else:
            self._ed_check_date_from.disable()
            self._ed_check_date_to.disable()
        self._refresh_tb_check()

    def _check_cancel(self):
        queue = 1
        cancel = 4
        self._logger.info("Check cancelling is running")
        check_id = self._tb_check.get_selected_id
        if not check_id:
            messagebox.showerror("Application error",
                                 "Проверка для отмены не выбрана")
            return
        if check_id == self.iv_current_check_id.get():
            messagebox.showerror("Application error",
                                 "Проверка выполняется, отмена невозможна")
            return
        try:
            status = self._driver.fact_check_rd_status(check_id)
            if not status or status[0] != queue:
                messagebox.showerror("Application error",
                                     "Отмена возможна только "
                                     "для проверки в очереди")
                return
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error", "Ошибка проверки статуса")
            return
        try:
            self._driver.fact_check_upd(check_id, datetime.datetime.now(),
                                        fact_check_obj_count=None,
                                        fact_check_status_id=cancel)
            self._refresh_tb_check()
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка обновления статуса проверки: {ex}")

    def _rerun_check(self):
        self._logger.info("Check rerun is running")
        check_id = self._tb_check.get_selected_id
        if not check_id:
            messagebox.showerror("Application error",
                                 "Проверка не выбрана")
            return
        script_id = None
        try:
            script_id = self._driver.fact_check_rd_script(check_id)[0]
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения скрипта из бд: {ex}")
        if not script_id:
            messagebox.showerror("Application error", "Скрипт не найден")
            return
        link = None
        try:
            link = self._driver.user_script_link_srch(self._user_id, script_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script saving error",
                                 f"Ошибка проверки видимости скрипта: {ex}")
        if not link:
            messagebox.showerror("Application error",
                                 "Скрипт не доступен текущему пользователю")
            return
        try:
            self._scr_queue.put(script_id, link[0])
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Script queue error",
                                 f"Ошибка добавления скрипта в очередь: {ex}")

    def _show_obj(self):
        check_id = self._tb_check.get_selected_id
        if not check_id:
            messagebox.showerror("Application error",
                                 "Проверка не выбрана")
            return
        self._iv_showed_check_id.set(check_id)
        self._reset_tb_obj_params()
        self._tab.select(3)

    def _on_upd_iv_showed_check_id(self, *args):
        check_id = self._iv_showed_check_id.get()
        if not check_id:
            return
        script_rec = None
        try:
            check_rec = self._driver.fact_check_rd(check_id)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка поиска проверки: {ex}")
        if check_rec:
            self._lbl_object_context.config(text="Выбранная проверка: "
                                                 f"\n{check_rec[0]} "
                                                 f"от {check_rec[3]}")
        else:
            self._lbl_object_context.config(text="Выбранная проверка: "
                                                 "не задана")

    def _get_object_tab(self):
        self._logger.info('Creating object tab')
        fr_obj_tab = tk.Frame(self)
        fr_obj_controls = tk.Frame(fr_obj_tab)
        fr_obj_controls.pack(side="left", fill="y", padx=10)
        self._lbl_object_context = tk.Label(fr_obj_controls,
                                            text="Выбранная проверка: "
                                                 "не задана")
        self._lbl_object_context.pack(fill="x", expand=True)
        fr_obj_filters = tk.Frame(fr_obj_controls)
        fr_obj_filters.pack(side="top", fill="both", expand=True)
        cb_all_user_obj = tk.Checkbutton(fr_obj_controls,
                                         text="Для всех пользователей",
                                         variable=self._iv_all_user_obj,
                                         padx=15)
        cb_all_user_obj.pack(fill="x", expand=True)
        cb_all_check_obj = tk.Checkbutton(fr_obj_controls,
                                          text="Для всех проверок",
                                          variable=self._iv_all_check_obj,
                                          padx=15)
        cb_all_check_obj.pack(fill="x", expand=True)
        rb_all_status_obj = tk.Radiobutton(fr_obj_controls,
                                           text="Любой статус", value=-1,
                                           variable=self._iv_status_obj,
                                           padx=15)
        rb_all_status_obj.pack(fill="x", expand=True)
        rb_tr_status_obj = tk.Radiobutton(fr_obj_controls, text="Trivial",
                                          value=1, variable=self._iv_status_obj,
                                          padx=15)
        rb_tr_status_obj.pack(fill="x", expand=True)
        rb_wr_status_obj = tk.Radiobutton(fr_obj_controls, text="Warning",
                                          value=2, variable=self._iv_status_obj,
                                          padx=15)
        rb_wr_status_obj.pack(fill="x", expand=True)
        rb_er_status_obj = tk.Radiobutton(fr_obj_controls, text="Error",
                                          value=3, variable=self._iv_status_obj,
                                          padx=15)
        rb_er_status_obj.pack(fill="x", expand=True)
        lbl_script_filter = tk.Label(fr_obj_controls,
                                     text="Поиск по названию скрипта")
        lbl_script_filter.pack(fill="x", expand=True)
        en_check_script_name = tk.Entry(fr_obj_controls,
                                        textvariable=self._sv_obj_script_name)
        en_check_script_name.pack(fill="x", expand=True)
        lbl_obj_filter = tk.Label(fr_obj_controls, text="Поиск по объекту")
        lbl_obj_filter.pack(fill="x", expand=True)
        en_obj_name = tk.Entry(fr_obj_controls, textvariable=self._sv_obj_name)
        en_obj_name.pack(fill="x", expand=True)
        cb_period_checks = tk.Checkbutton(fr_obj_controls,
                                          text="По проерке за период",
                                          variable=self._iv_period_checks_obj,
                                          padx=15, pady=10)
        cb_period_checks.pack(fill="x", expand=True)
        self._ed_check_obj_date_from = DateEntry(fr_obj_controls,
                                                 self._log_config,
                                                 "с  ",
                                                 command=self._refresh_tb_obj)
        self._ed_check_obj_date_from.pack(fill="x", expand=True)
        self._ed_check_obj_date_from.disable()
        self._ed_check_obj_date_to = DateEntry(fr_obj_controls,
                                               self._log_config,
                                               "по ",
                                               command=self._refresh_tb_obj)
        self._ed_check_obj_date_to.pack(fill="x", expand=True)
        self._ed_check_obj_date_to.disable()
        cb_period_obj = tk.Checkbutton(fr_obj_controls,
                                       text="По объекту за период",
                                       variable=self._iv_period_obj,
                                       padx=15, pady=10)
        cb_period_obj.pack(fill="x", expand=True)
        self._ed_obj_date_from = DateEntry(fr_obj_controls,
                                           self._log_config,
                                           "с  ",
                                           command=self._refresh_tb_obj)
        self._ed_obj_date_from.pack(fill="x", expand=True)
        self._ed_obj_date_from.disable()
        self._ed_obj_date_to = DateEntry(fr_obj_controls,
                                         self._log_config,
                                         "по ",
                                         command=self._refresh_tb_obj)
        self._ed_obj_date_to.pack(fill="x", expand=True)
        self._ed_obj_date_to.disable()
        fr_obj_btns = tk.Frame(fr_obj_controls)
        fr_obj_btns.pack(side="top", fill="both", expand=True)
        page_cnt = self._get_page_cnt(self._driver.object_cnt,
                                      self._config["tb_object_row_limit"],
                                      user_id=None, fact_check_id=None,
                                      error_level_id=None,
                                      object_name_pattern=None,
                                      script_name_pattern=None,
                                      fact_check_end_date_from=None,
                                      fact_check_end_date_to=None,
                                      object_date_from=None,
                                      object_date_to=None)
        self._pgn_obj = Pagination(fr_obj_controls, 3, page_cnt,
                                   prev_button="<<",
                                   next_button=">>",
                                   command=self._load_obj_page,
                                   pagination_style=self._config[
                                         "pagination_style"])
        self._pgn_obj.pack(side="bottom", fill="both", expand=True)
        self._tb_obj = Table(fr_obj_tab,
                             headings=("id", "Название скрипта",
                                       "Пользователь",
                                       "Дата выполнения проверки",
                                       "Название объекта",
                                       "Идентификатор объекта",
                                       "Комментарий",
                                       "Автор",
                                       "Дата объекта",
                                       "Уровень реагирования"))
        self._tb_obj.pack(side="right", fill="both", expand=True)
        self._load_obj_page(1)
        return fr_obj_tab

    def _refresh_tb_obj(self, *args):
        self._logger.debug("Refreshing tb_obj is running")
        cur_page = self._pgn_obj.current_page
        cur_page_cnt = self._pgn_obj.total_pages
        user_id = None if self._iv_all_user_obj.get() else self._user_id
        check_id = None if self._iv_all_check_obj.get() \
            else self._iv_showed_check_id.get()
        error_level_id = self._iv_status_obj.get()
        error_level_id = None if error_level_id == -1 else error_level_id
        obj_name_pattern = None
        value = self._sv_obj_name.get()
        if value and value.strip():
            obj_name_pattern = value
        script_name_pattern = None
        value = self._sv_obj_script_name.get()
        if value and value.strip():
            script_name_pattern = value
        fact_check_end_date_from = self._ed_check_obj_date_from.get()
        fact_check_end_date_to = self._ed_check_obj_date_to.get()
        object_date_from = self._ed_obj_date_from.get()
        object_date_to = self._ed_obj_date_to.get()
        page_cnt = self._get_page_cnt(self._driver.object_cnt,
                                      self._config["tb_object_row_limit"],
                                      user_id=user_id,
                                      fact_check_id=check_id,
                                      error_level_id=error_level_id,
                                      object_name_pattern=obj_name_pattern,
                                      script_name_pattern=script_name_pattern,
                                      fact_check_end_date_from=
                                      fact_check_end_date_from,
                                      fact_check_end_date_to=
                                      fact_check_end_date_to,
                                      object_date_from=object_date_from,
                                      object_date_to=object_date_to)
        page_cnt = max(1, page_cnt)
        if cur_page_cnt != page_cnt:
            cur_page = min(cur_page, page_cnt)
            self._pgn_obj.update(page_cnt, cur_page)
        self._load_obj_page(cur_page)

    def _on_upd_iv_period_checks_obj(self, *args):
        if self._iv_period_checks_obj.get():
            self._ed_check_obj_date_from.enable()
            self._ed_check_obj_date_to.enable()
        else:
            self._ed_check_obj_date_from.disable()
            self._ed_check_obj_date_to.disable()
        self._refresh_tb_obj()

    def _on_upd_iv_period_obj(self, *args):
        if self._iv_period_obj.get():
            self._ed_obj_date_from.enable()
            self._ed_obj_date_to.enable()
        else:
            self._ed_obj_date_from.disable()
            self._ed_obj_date_to.disable()
        self._refresh_tb_obj()

    def _load_obj_page(self, page_num):
        limit = self._config["tb_object_row_limit"]
        offset = (page_num - 1) * limit
        user_id = None if self._iv_all_user_obj.get() else self._user_id
        check_id = None if self._iv_all_check_obj.get()\
            else self._iv_showed_check_id.get()
        error_level_id = self._iv_status_obj.get()
        error_level_id = None if error_level_id == -1 else error_level_id
        obj_name_pattern = None
        value = self._sv_obj_name.get()
        if value and value.strip():
            obj_name_pattern = value
        script_name_pattern = None
        value = self._sv_obj_script_name.get()
        if value and value.strip():
            script_name_pattern = value
        fact_check_end_date_from = self._ed_check_obj_date_from.get()
        fact_check_end_date_to = self._ed_check_obj_date_to.get()
        object_date_from = self._ed_obj_date_from.get()
        object_date_to = self._ed_obj_date_to.get()
        obj_rec = None
        try:
            obj_rec = self._driver.object_rd_pg(limit, offset, user_id,
                                                check_id, error_level_id,
                                                obj_name_pattern,
                                                script_name_pattern,
                                                fact_check_end_date_from,
                                                fact_check_end_date_to,
                                                object_date_from,
                                                object_date_to)
        except Exception as ex:
            self._logger.exception(ex)
            messagebox.showerror("Data base error",
                                 f"Ошибка чтения объектов из БД: {ex}")
        self._tb_obj.clear()
        if obj_rec:
            self._tb_obj.insert(obj_rec)

    def _reset_tb_obj_params(self):
        self._iv_all_user_obj.set(1)
        self._iv_all_check_obj.set(0)
        self._iv_status_obj.set(-1)
        self._iv_period_checks_obj.set(0)
        self._iv_period_obj.set(0)
        self._sv_obj_name.set("")
        self._sv_obj_script_name.set("")
