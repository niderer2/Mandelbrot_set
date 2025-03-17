import tkinter as tk
from tkinter import filedialog, colorchooser
import subprocess
import os

def fifa(n):
    if n:
        return 'y'
    return 'n'

def choose_color(index):
    color = colorchooser.askcolor()[0]  # Получаем RGB кортеж
    if color:
        color_vars[index].set(f"{int(color[0])} {int(color[1])} {int(color[2])}")

def generate_mandelbrot():
    script_path = os.path.join(os.path.dirname(__file__), "Множество Мондельброта.py")
    if not os.path.exists(script_path):
        status_label.config(text="Ошибка: Файл 'Множество Мондельброта.py' не найден!")
        return
    
    params = [
        'tyjknbvcdfghnbvfrgthkg,vmmn',
        variables[0].get() or "name",
        variables[1].get(),
        variables[2].get(),
        color_vars1.get(),  # Первый цвет
        color_vars2.get(),  # Второй цвет
        color_vars3.get(),  # Третий цвет
        variables[3].get(),
        variables[4].get(),
        variables[5].get(),
        variables[6].get(),
        variables[7].get(),
        variables[8].get(),
        variables[9].get(),
        variables[10].get(),
        fifa(unstable_var.get()),
        variables[11].get(),
    ]
    
    try:
        process = subprocess.Popen(["python", script_path], stdin=subprocess.PIPE, text=True)
        process.communicate("\n".join(params))  # Передаем параметры построчно
        status_label.config(text="Изображение успешно сгенерировано!")
    except subprocess.CalledProcessError as e:
        status_label.config(text=f"Ошибка выполнения: {e}")

root = tk.Tk()
root.title("Настройки множества Мандельброта")

params_info = [
    ("Название файла", "name"),
    ("Размеры картинки (Ширина Высота)", "1000 1000"),
    ("Градиент (кол-во цветов)", "100"),
    ("Множитель степени и точки", "2.0 1.0"),
    ("Прибавляемая константа", "0.0"),
    ("Множитель к сумме итерации (степень, значение, константа)", "0.0 0.0 0.0"),
    ('Множитель множителя синуса итогового значения', '0'),
    ("Границы множества", "2.0"),
    ("Макс. итерации", "1000"),
    ("Приближение", "1.0"),
    ("Сдвиг (X Y)", "0.0 0.0"),
    ('Степень для нестабильного оператора (степень, множитель, константа)', "1.0 1.0 1.0")
]

variables = []

for i, (label, default) in enumerate(params_info):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w')
    var = tk.StringVar(value=default)
    tk.Entry(root, textvariable=var).grid(row=i, column=1)
    variables.append(var)

# Добавляем выбор трех цветов
color_vars1 = tk.StringVar(value="4 0 84")
color_vars2 = tk.StringVar(value="219 222 202")
color_vars3 = tk.StringVar(value="255 0 0")
color_labels = ["Цвет 1", "Цвет 2", "Цвет 3"]

for i in range(3):
    tk.Label(root, text=color_labels[i]).grid(row=len(params_info) + i, column=0, sticky='w')
    tk.Button(root, text="Выбрать цвет", command=lambda i=i: choose_color(i)).grid(row=len(params_info) + i, column=1)

# Чекбокс в конце формы
unstable_var = tk.IntVar()
label = tk.Label(root, text="Нестабильный итератор:")
label.grid(row=len(params_info) + 3, column=0, sticky="w", padx=5, pady=5)
checkbox = tk.Checkbutton(root, variable=unstable_var)
checkbox.grid(row=len(params_info) + 3, column=1, sticky="w", padx=5, pady=5)

# Кнопка запуска
tk.Button(root, text="Запустить генерацию", command=generate_mandelbrot).grid(row=len(params_info) + 4, column=0, columnspan=2)
status_label = tk.Label(root, text="")
status_label.grid(row=len(params_info) + 5, column=0, columnspan=2)

root.mainloop()
