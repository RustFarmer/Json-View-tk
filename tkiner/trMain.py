# -*- coding: utf-8 -*-
import json
import tkinter
import os
from loguru import logger
from typing import Any, Union, Dict, List
from tkinter import *
from tkinter import Tk, ttk, filedialog
from tkinter.messagebox import showerror, showinfo

file_name = 'tkiner/settingsProgram.json'
version = 1.0
avtorname: str = '星空の下で-----'
flag_change_config = 0

with open(file_name, 'r', encoding='utf-8') as file:
    data = json.load(file)


def find_setting(data, target_key):
    """
    Рекурсивно ищет значение настройки по ключу во вложенных структурах JSON.
    """
    if isinstance(data, dict):
        if target_key in data:
            return data[target_key]
        for key, value in data.items():
            result = find_setting(value, target_key)
            if result is not None:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_setting(item, target_key)
            if result is not None:
                return result
    return None


def search_json(data, target_key=None, target_value=None, return_paths=False):
    """
    Универсальный поиск в JSON.
    - Если задан target_key – возвращает все значения для этого ключа.
    - Если задан target_value – возвращает все ключи (или пути), где значение совпадает.
    - Если заданы оба – возвращает пары (путь, значение) для ключа, у которого значение равно target_value.
    - return_paths=True – возвращать пути вместо просто значений.
    """
    results = []

    def traverse(obj, path=()):
        if isinstance(obj, dict):
            for key, val in obj.items():
                current_path = (*path, key)
                # Проверяем условия
                if target_key is not None and target_value is not None:
                    if key == target_key and val == target_value:
                        results.append((current_path, val) if return_paths else val)
                elif target_key is not None:
                    if key == target_key:
                        results.append((current_path, val) if return_paths else val)
                elif target_value is not None:
                    if val == target_value:
                        results.append((current_path, val) if return_paths else key)
                traverse(val, current_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                traverse(item, (*path, idx))

    traverse(data)
    return results


def modify_all_key_values(file_path: str, key_name: str, new_value: Any):
    """
    Изменяет значения всех ключей с указанным названием в JSON файле.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def modify_key_values_recursive(obj: Union[Dict, List], target_key: str, value: Any):
        if isinstance(obj, dict):
            for key in obj:
                if key == target_key:
                    obj[key] = value
                else:
                    modify_key_values_recursive(obj[key], target_key, value)
        elif isinstance(obj, list):
            for item in obj:
                modify_key_values_recursive(item, target_key, value)

    modify_key_values_recursive(data, key_name, new_value)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def add_work_file_path(config_file_path: str, new_path: str):
    """
    Добавляет новый путь в массив work_file_path внутри JSON-файла настроек.
    Если ключа нет или он не список – создаёт список.
    """
    with open(config_file_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    if not isinstance(cfg.get("work_file_path"), list):
        old = cfg.get("work_file_path")
        cfg["work_file_path"] = [old] if old else []

    if new_path not in cfg["work_file_path"]:
        cfg["work_file_path"].append(new_path)

    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


class AppConfig:

    @staticmethod
    def get_config_path():
        """
        Возвращает путь к рабочему файлу конфигурации.
        Если в settings_flag == 1 и work_file_path не пуст – берёт последний путь.
        Иначе открывает диалог выбора, добавляет выбранный путь в список и устанавливает флаг.
        """
        global flag_change_config, data

        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

        SETTINGS_FLAG = bool(int(find_setting(data, "settings_flag")))
        WORK_PATHS = find_setting(data, 'work_file_path')

        if SETTINGS_FLAG and isinstance(WORK_PATHS, list) and len(WORK_PATHS) > 0:
            return WORK_PATHS[-1]

        root = tkinter.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Выберите файл конфигурации Rust (обычно .cfg файл)",
            filetypes=[("Config files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            logger.info("Путь не выбран. Приложение будет закрыто.")
            exit()

        add_work_file_path(file_name, file_path)
        modify_all_key_values(file_name, "settings_flag", "1")

        root.destroy()
        flag_change_config = 0
        return file_path


class Screen:
    def __init__(self):
        self.tree = None
        self.file_menu = None
        self.main_menu = None
        self.root = None
        self.history_menu = None
        self.current_file_path = None

        self.width = None
        self.height = None
        self.min_width = None
        self.min_height = None

        self.title: str = 'JsonWork'

    def __int__(self):
        return {self.width}, {self.height}, {self.min_width}, {self.min_height}

    def __str__(self):
        return self.title

    def set_width(self, width: int = 1899898) -> int:
        try:
            if width == 1899898:
                self.width = find_setting(data, "width")
                return self.width
            if width >= self.min_width:
                showerror(title=self.title, message="the window size should not be less than necessary.")
            else:
                self.width = width
                showinfo(title=self.title)
                return self.width
        except ValueError:
            showerror(title=self.title, message="the window size should be int")
        except TypeError as error:
            showerror(title=self.title, message=f'{error}')
        except BaseException as base_error:
            showerror(title=self.title, message=f"{base_error}")

    def set_height(self, height: int = 1899898) -> int:
        try:
            if height == 1899898:
                self.height = find_setting(data, "height")
                return self.height
            if height >= self.min_height:
                showerror(title=self.title, message="the window size should not be less than necessary.")
            else:
                self.height = height
                showinfo(title=self.title)
                return self.height
        except ValueError:
            showerror(title=self.title, message="the window size should be int")
        except TypeError as error:
            showerror(title=self.title, message=f'{error}')
        except BaseException as base_error:
            showerror(title=self.title, message=f"{base_error}")

    def __get_width__(self) -> int:
        return self.width

    def __get_height__(self) -> int:
        return self.height

    def display_file_content(self, file_path: str) -> None:
        """Загружает JSON из file_path и отображает его в таблице ключ-значение."""
        if not os.path.exists(file_path):
            print(f"File {file_path} not found.")
            showerror(title=self.title, message=f"File {file_path} not found.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON in a file {file_path}: {e}")
            showerror(title=self.title, message=f'Error parsing JSON in a file {file_path}: {e}')
            return
        except Exception as e:
            print(f"Unknown error while reading the file:: {e}")
            showerror(title=self.title, message=f'Unknown error while reading the file: {e}')
            return

        if self.tree:
            self.tree.destroy()
            self.tree = None

        self.tree = ttk.Treeview(self.root, columns=("Key", "Value"), show="headings")
        self.tree.heading("Key", text="Ключ")
        self.tree.heading("Value", text="Значение")
        self.tree.column("Key", width=200, stretch=True)
        self.tree.column("Value", width=300, stretch=True)

        def flatten(obj, parent_key='', sep='.') -> list:
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, (dict, list)):
                        items.extend(flatten(v, new_key, sep))
                    else:
                        items.append((new_key, str(v)))
            elif isinstance(obj, list):
                for idx, v in enumerate(obj):
                    new_key = f"{parent_key}[{idx}]"
                    if isinstance(v, (dict, list)):
                        items.extend(flatten(v, new_key, sep))
                    else:
                        items.append((new_key, str(v)))
            else:
                items.append((parent_key, str(obj)))
            return items

        flat_items = flatten(new_data)

        for key, value in flat_items:
            self.tree.insert('', END, values=(key, value))

        self.tree.pack(fill=BOTH, expand=1)
        self.current_file_path = file_path
        print(f"The table has been updated from the file {file_path}")

    def load_file(self, file_path: str):
        """Загружает файл по указанному пути и обновляет таблицу (меню НЕ перестраивает)."""
        if file_path and os.path.exists(file_path):
            self.display_file_content(file_path)

    def update_history_menu(self):
        """Перестраивает подменю 'History' на основе текущего списка work_file_path."""
        if not self.history_menu:
            return

        self.history_menu.delete(0, END)

        paths = find_setting(data, 'work_file_path')
        if paths and isinstance(paths, list) and paths:
            for path in paths:
                display_name = path if len(path) < 50 else '...' + path[-47:]
                self.history_menu.add_command(
                    label=display_name,
                    command=lambda p=path: self.load_file(p)
                )
            self.history_menu.add_separator()
        else:
            self.history_menu.add_command(label="(нет сохранённых файлов)", state="disabled")

        self.history_menu.add_command(label="Open new...", command=self.open_new_file)

    def open_new_file(self):
        """Открывает диалог выбора файла, добавляет путь и обновляет таблицу/меню."""
        global flag_change_config, data

        root = tkinter.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Выберите файл конфигурации",
            filetypes=[("Config files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            add_work_file_path(file_name, file_path)
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.update_history_menu()
            self.load_file(file_path)
        root.destroy()
        flag_change_config = 0

    @staticmethod
    def help_screen():
        help_root = Tk()
        help_text = 'The application is designed to provide a convenient visual' \
                    ' representation of JSON files.' \
                    '\nInstead of dealing with raw code, you get a structured' \
                    ' table view where each key and its corresponding value' \
                    ' are displayed in two columns.' \
                    '\nThe program is particularly useful when working' \
                    ' with configuration files, large datasets, or when ' \
                    'you need to quickly analyze the structure of a JSON file.'
        notebook = ttk.Notebook(help_root)

        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General information")

        general_text = Text(general_frame, wrap=WORD, padx=10, pady=10)
        general_text.insert(END, help_text)
        general_text.config(state=DISABLED)
        general_text.pack(fill=BOTH, expand=True)
        notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="About the program")

        about_text = Text(about_frame, wrap=WORD, padx=10, pady=10)
        about_text.insert(END,
                          f"Version {version}\n\n"
                          f"Author: {avtorname}\n"
                          f"GitHub: https://github.com/RustFarmer/Rust-helper\n"
                          "Release date: 2026"
                          )
        about_text.config(state=DISABLED)
        about_text.pack(fill=BOTH, expand=True)
        close_btn = ttk.Button(help_root, text="Закрыть", command=help_root.destroy)
        close_btn.pack(pady=10)

    def menu(self) -> object:
        self.main_menu = Menu()
        self.file_menu = Menu()

        self.history_menu = Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="History", menu=self.history_menu)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open", command=self.open_new_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.main_menu.add_cascade(label="History", menu=self.history_menu)
        self.main_menu.add_cascade(label="help", command=self.help_screen)

        self.update_history_menu()
        return self.main_menu

    def start_program(self):
        self.set_width()
        self.set_height()

        self.root = Tk()
        self.root.option_add("*tearOff", FALSE)

        self.root.geometry(f'{self.width}x{self.height}')
        self.root.title(self.title)

        self.root.config(menu=self.menu())

        ss = find_setting(data, 'work_file_path')
        if ss and isinstance(ss, list) and ss:
            self.load_file(ss[-1])
        else:
            self.open_new_file()

        self.root.mainloop()
