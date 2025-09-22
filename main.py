import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import re
from datetime import datetime
import random
import string

def clean_name(name):
    """Удаляет недопустимые символы из имени"""
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '', name.strip())

def create_items(is_folder):
    """Создает папки или файлы по списку имен"""
    # Проверяем выбранную папку
    result_base = result_base_path.get()
    if not result_base:
        messagebox.showerror("Ошибка", "Не выбрана базовая папка для создания Result")
        return
    
    content = text_area.get("1.0", tk.END).strip()
    
    # Получаем список имен
    if content:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        bad_lines = []
        names = []
        for line in lines:
            cleaned = clean_name(line)
            if cleaned:
                names.append(cleaned)
            else:
                bad_lines.append(line)
        if bad_lines:
            messagebox.showwarning("Предупреждение", 
                                 "Следующие строки состояли только из недопустимых символов (не созданы):\n\n" +
                                 "\n".join(bad_lines) + "\n\n" +
                                 "Запрещенные символы для имен файлов/папок: < > : \" / \\ | ? *")
    else:
        if is_folder:
            path = folder_path.get()
        else:
            path = file_path.get()
            
        if not path:
            messagebox.showerror("Ошибка", f"Не выбран файл для {'папок' if is_folder else 'файлов'} или не введен список")
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                bad_lines = []
                names = []
                for line in lines:
                    cleaned = clean_name(line)
                    if cleaned:
                        names.append(cleaned)
                    else:
                        bad_lines.append(line)
                if bad_lines:
                    messagebox.showwarning("Предупреждение", 
                                         "Следующие строки состояли только из недопустимых символов (не созданы):\n\n" +
                                         "\n".join(bad_lines) + "\n\n" +
                                         "Запрещенные символы для имен файлов/папок: < > : \" / \\ | ? *")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл: {e}")
            return
    
    if not names:
        messagebox.showwarning("Предупреждение", "Список пуст")
        return
    
    # Создаем папку Result в выбранной базовой папке (только если не существует)
    result_dir = os.path.join(result_base, "Result")
    try:
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать папку Result в '{result_base}': {e}")
        return
    
    created_count = 0
    extension = file_extension.get().strip() or ".txt"
    fill_mode = fill_var.get()
    min_bytes = min_bytes_var.get()
    max_bytes = max_bytes_var.get()
    if min_bytes > max_bytes:
        messagebox.showerror("Ошибка", "Минимальный размер не может быть больше максимального")
        return
    for name in names:
        full_path = os.path.join(result_dir, name)
        try:
            if is_folder:
                os.makedirs(full_path, exist_ok=True)
                created_count += 1
            else:
                full_path += extension
                with open(full_path, 'w', encoding='utf-8') as f:
                    if fill_mode == "yes":
                        size = random.randint(min_bytes, max_bytes)
                        content = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))
                        f.write(content)
                    else:
                        f.write(f"Файл {name} создан {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                created_count += 1
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать '{name}': {e}")
            continue
    
    messagebox.showinfo("Готово!", 
                       f"Создано {created_count} {'папок' if is_folder else 'файлов'}\n"
                       f"в папке '{result_dir}'")

def load_file(is_folder):
    """Загружает txt файл со списком"""
    path = filedialog.askopenfilename(
        title=f"Выберите файл со списком {'папок' if is_folder else 'файлов'}",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if path:
        if is_folder:
            folder_path.set(path)
            file_path.set("")  # Очищаем поле для файлов
            # Автоматически вставляем содержимое в текстовое поле
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert("1.0", f.read())
            except:
                pass
        else:
            file_path.set(path)
            folder_path.set("")  # Очищаем поле для папок
            # Автоматически вставляем содержимое в текстовое поле
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert("1.0", f.read())
            except:
                pass

def select_result_base():
    """Выбирает базовую папку для Result"""
    path = filedialog.askdirectory(title="Выберите папку, где будет создана Result")
    if path:
        result_base_path.set(path)

def generate_list():
    gen_type = gen_var.get()
    text_area.delete("1.0", tk.END)
    if gen_type == "numbers":
        try:
            max_num = int(max_num_var.get())
            for i in range(1, max_num + 1):
                text_area.insert(tk.END, f"{i}\n")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число для 'от 1 до'")
    elif gen_type == "letters":
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            text_area.insert(tk.END, f"{letter}\n")

def apply_prefix_suffix():
    prefix = prefix_var.get().strip()
    suffix = suffix_var.get().strip()
    
    # Проверяем префикс и суффикс
    if not clean_name(prefix) == prefix:
        messagebox.showwarning("Предупреждение", 
                             "Недопустимые символы в префиксе:\n'" + prefix + "'\n\n" +
                             "Запрещенные символы для имен файлов/папок: < > : \" / \\ | ? *\n" +
                             "Префикс не применен.")
        return
    if not clean_name(suffix) == suffix:
        messagebox.showwarning("Предупреждение", 
                             "Недопустимые символы в суффиксе:\n'" + suffix + "'\n\n" +
                             "Запрещенные символы для имен файлов/папок: < > : \" / \\ | ? *\n" +
                             "Суффикс не применен.")
        return
    
    content = text_area.get("1.0", tk.END).strip()
    if not content:
        return
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    bad_lines = []
    new_names = []
    for line in lines:
        new_name = f"{prefix}{line}{suffix}"
        cleaned = clean_name(new_name)
        if cleaned:
            new_names.append(cleaned)
        else:
            bad_lines.append(line)
    if bad_lines:
        messagebox.showwarning("Предупреждение", 
                             "Следующие строки после применения стали пустыми (не применены):\n\n" +
                             "\n".join(bad_lines) + "\n\n" +
                             "Запрещенные символы для имен файлов/папок: < > : \" / \\ | ? *")
    text_area.delete("1.0", tk.END)
    for name in new_names:
        text_area.insert(tk.END, f"{name}\n")

def toggle_fill_fields():
    state = "normal" if fill_var.get() == "yes" else "disabled"
    min_bytes_entry.config(state=state)
    max_bytes_entry.config(state=state)

def clear_fields():
    """Очищает все поля ввода"""
    folder_path.set("")
    file_path.set("")
    text_area.delete("1.0", tk.END)
    prefix_var.set("")
    suffix_var.set("")
    max_num_var.set("1000")
    file_extension.set(".txt")
    result_base_path.set("")
    fill_var.set("no")
    min_bytes_var.set(0)
    max_bytes_var.set(1048576)
    toggle_fill_fields()

# Создание окна
root = tk.Tk()
root.title("Создание файлов и папок - FileFolderGen 1.0")
root.geometry("550x750")
root.resizable(True, True)

# Заголовок
title_label = tk.Label(root, text="Создание файлов и папок", 
                      font=("Arial", 14, "bold"))
title_label.pack(pady=10)

# Выбор базовой папки для Result
base_frame = tk.LabelFrame(root, text="Базовая папка для Result", font=("Arial", 9, "bold"))
base_frame.pack(pady=5, padx=10, fill="x")

result_base_frame = tk.Frame(base_frame)
result_base_frame.pack(fill="x", padx=5, pady=5)
result_base_path = tk.StringVar()
tk.Entry(result_base_frame, textvariable=result_base_path, width=45).pack(side="left", fill="x", expand=True)
tk.Button(result_base_frame, text="Выбрать", 
          command=select_result_base).pack(side="right", padx=(5,0))

# Загрузка списков из файлов
file_frame = tk.LabelFrame(root, text="Загрузка списков из файлов", font=("Arial", 9, "bold"))
file_frame.pack(pady=5, padx=10, fill="x")

folder_frame = tk.Frame(file_frame)
folder_frame.pack(fill="x", padx=5, pady=2)
folder_path = tk.StringVar()
tk.Entry(folder_frame, textvariable=folder_path, width=35).pack(side="left", fill="x", expand=True)
tk.Button(folder_frame, text="Папки", 
          command=lambda: load_file(True)).pack(side="right", padx=(5,0))

file_frame2 = tk.Frame(file_frame)
file_frame2.pack(fill="x", padx=5, pady=2)
file_path = tk.StringVar()
tk.Entry(file_frame2, textvariable=file_path, width=35).pack(side="left", fill="x", expand=True)
tk.Button(file_frame2, text="Файлы", 
          command=lambda: load_file(False)).pack(side="right", padx=(5,0))

# Инструменты для редактора
editor_tools_frame = tk.LabelFrame(root, text="Инструменты редактора", font=("Arial", 9, "bold"))
editor_tools_frame.pack(pady=5, padx=10, fill="x")

# Генерация списка
gen_frame = tk.Frame(editor_tools_frame)
gen_frame.pack(fill="x", padx=5, pady=2)
gen_var = tk.StringVar(value="numbers")
tk.Radiobutton(gen_frame, text="Числа 1-", variable=gen_var, value="numbers").pack(side="left")
max_num_var = tk.StringVar(value="1000")
tk.Entry(gen_frame, textvariable=max_num_var, width=8).pack(side="left", padx=2)
tk.Radiobutton(gen_frame, text="A-Z", variable=gen_var, value="letters").pack(side="left", padx=5)
tk.Button(gen_frame, text="Заполнить", command=generate_list).pack(side="left", padx=2)

# Префиксы/суффиксы
prefix_frame = tk.Frame(editor_tools_frame)
prefix_frame.pack(fill="x", padx=5, pady=2)
tk.Label(prefix_frame, text="Префикс:").pack(side="left")
prefix_var = tk.StringVar()
tk.Entry(prefix_frame, textvariable=prefix_var, width=12).pack(side="left", padx=2)
tk.Label(prefix_frame, text="Суффикс:").pack(side="left")
suffix_var = tk.StringVar()
tk.Entry(prefix_frame, textvariable=suffix_var, width=12).pack(side="left", padx=2)
tk.Button(prefix_frame, text="Применить", command=apply_prefix_suffix).pack(side="left", padx=2)

# Расширение для файлов
ext_frame = tk.Frame(editor_tools_frame)
ext_frame.pack(fill="x", padx=5, pady=2)
tk.Label(ext_frame, text="Расширение:").pack(side="left")
file_extension = tk.StringVar(value=".txt")
tk.Entry(ext_frame, textvariable=file_extension, width=8).pack(side="left", padx=2)

# Заполнение файлов
fill_frame = tk.LabelFrame(root, text="Заполнение файлов", font=("Arial", 9, "bold"))
fill_frame.pack(pady=5, padx=10, fill="x")

fill_var = tk.StringVar(value="no")
tk.Radiobutton(fill_frame, text="Не заполнять", variable=fill_var, value="no", command=toggle_fill_fields).pack(side="left", padx=5)
tk.Radiobutton(fill_frame, text="Заполнять", variable=fill_var, value="yes", command=toggle_fill_fields).pack(side="left", padx=5)

size_frame = tk.Frame(fill_frame)
size_frame.pack(pady=5, fill="x")
tk.Label(size_frame, text="От (байты):").pack(side="left", padx=5)
min_bytes_var = tk.IntVar(value=0)
min_bytes_entry = tk.Entry(size_frame, textvariable=min_bytes_var, width=8, state="disabled")
min_bytes_entry.pack(side="left", padx=2)
tk.Label(size_frame, text="До:").pack(side="left", padx=5)
max_bytes_var = tk.IntVar(value=1048576)
max_bytes_entry = tk.Entry(size_frame, textvariable=max_bytes_var, width=8, state="disabled")
max_bytes_entry.pack(side="left", padx=2)

# Текстовое поле для ручного ввода
text_frame = tk.LabelFrame(root, text="Список имен", font=("Arial", 9, "bold"))
text_frame.pack(pady=5, padx=10, fill="both", expand=True)

text_area = scrolledtext.ScrolledText(text_frame, height=8, width=60, wrap=tk.WORD)
text_area.pack(padx=5, pady=5, fill="both", expand=True)

# Кнопки действий
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Создать папки", 
          command=lambda: create_items(True),
          bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
          width=12, height=1).pack(side="left", padx=3)

tk.Button(button_frame, text="Создать файлы", 
          command=lambda: create_items(False),
          bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
          width=12, height=1).pack(side="left", padx=3)

tk.Button(button_frame, text="Очистить", 
          command=clear_fields,
          bg="#f44336", fg="white", font=("Arial", 10, "bold"),
          width=10, height=1).pack(side="left", padx=3)

# Информация
info_label = tk.Label(root, text="В выбранной папке будет создана папка 'Result'\n"
                                 "Запрещенные символы: < > : \" / \\ | ? *", 
                     font=("Arial", 8), fg="gray", justify=tk.LEFT)
info_label.pack(pady=5)

root.mainloop()