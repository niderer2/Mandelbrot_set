import tkinter as tk
from tkinter import filedialog, colorchooser
import subprocess
import os

def fifa(n):
    k = []
    for i in n:
        k.append(str(i.get()))
    return k

def remove_n(n):
    k = ''
    for i in str(n):
        if i not in (')', '('):
            k = k + i
    return k

def choose_color(index):
    color = colorchooser.askcolor()[0]  # Получаем RGB кортеж
    if color:
        color_vars[index].set(f"{int(color[0])} {int(color[1])} {int(color[2])}")

def generate_mandelbrot():
    script_path = os.path.join(os.path.dirname(__file__), "Множество Мондельброта.py")
    if not os.path.exists(script_path):
        status_label.config(text="Ошибка: Файл 'Множество Мондельброта.py' не найден")
        return
    
    params = [
        variables[0].get() or "name", # имя
        variables[1].get(), # размеры
        variables[2].get(), # кол-во цветов
        color_vars1.get(),  # Первый цвет
        color_vars2.get(),  # Второй цвет
        color_vars3.get(),  # Третий цвет
        remove_n(variables[3].get()), # множитель степени и точки
        remove_n(variables[4].get()), # константа
        remove_n(variables[5].get()), # Множитель к костанте
        remove_n(variables[6].get()), # Множитель синуса
        remove_n(variables[7].get()), # Множитель косинуса
        remove_n(variables[8].get()), # Граница
        remove_n(variables[9].get()), # Макс кол-во интераций
        remove_n(variables[10].get()), # Сдвиг
        remove_n(variables[11].get()), # Приближение
        ' '.join(fifa(vare_var[0])), # Нестабильный оператор
        remove_n(variables[12].get()), # Степень для нестабильного оператора
        ' '.join(fifa(vare_var[1])), # Модули (Общей фукции, Tригонометрические фукции, z, с)
        ' '.join(fifa(vare_var[2])), # Модуль z (x, y)
        ' '.join(fifa(vare_var[3])), # Модуль с (x, y)
        ' '.join(fifa(vare_var[4])), # Отсудвие вращения при возведении на мнимое число
        ' '.join(fifa(vare_var[5])), # Вкл. общий вид при мнимой части в множителя точки
        ' '.join(fifa(vare_var[6])), # Умножение по отдельности
    ]
    try:
        process = subprocess.Popen(["python", script_path], stdin=subprocess.PIPE, text=True)
        #print(' '.join(fifa(vare_var[1])))
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
    ("Множитель степени и точки", "(2.0 0.0) (1.0 0.0)"),
    ("Прибавляемая константа", "(0.0 0.0)"),
    ("Множитель к сумме итерации (степень, значение, константа)", "(0.0 0.0) (0.0 0.0) (0.0 0.0)"),
    ('Множитель синуса (степень, множитель, сумма)', '(1.0 0.0) (0.0 0.0) (0.0 0.0)'),
    ('Множитель косинуса (степень, множитель, сумма)', '(1.0 0.0) (0.0 0.0) (0.0 0.0)'),
    ("Границы множества", "2"),
    ("Макс. итерации", "1000"),
    ("Приближение", "1.0"),
    ("Сдвиг (X Y)", "0.0 0.0"),
    ('Степень для нестабильного оператора (степень, множитель, константа)', "(1.0 0.0) (1.0 0.0) (1.0 0.0)")
]

variables = []

for i, (label, default) in enumerate(params_info):
    tk.Label(root, text=label).grid(row=i, column=0, sticky='w')
    var = tk.StringVar(value=default)
    tk.Entry(root, textvariable=var).grid(row=i, column=1)
    variables.append(var)

class CheckboxColumn:
    global params_info
    
    def __init__(self, root, start_row=len(params_info)):
        self.root = root
        self.start_row = start_row
        self.variables = []
    def create_checkbox(self, text, count=1):
        row = self.start_row
        label = tk.Label(self.root, text=text)
        label.grid(row=row, column=0, padx=0, pady=0, sticky="w")
        vars_group = []
        for i in range(count):
            var = tk.IntVar(value=0)
            vars_group.append(var)
            chk = tk.Checkbutton(self.root, variable=var)
            chk.grid(row=row, column=i + 2, padx=0, pady=1, sticky="w")
        self.variables.append(vars_group)
        self.start_row += 1
        return vars_group

checkbox_column = CheckboxColumn(root)
unstable_var = [('Нестабильный оператор', 1),
                ("Модуль (Общей фукции, Tригонометрические фукции, z, с)", 4),
                ("Модуль z (x, y)", 2),
                ("Модуль с (x, y)", 2),
                ("Отсудвие вращения при возведении на мнимое число", 1),
                ("Вкл. общий вид при мнимой части в множителя точки", 1),
                ("умножение по отдельности", 1)] 

vare_var = []
for txt, i in unstable_var:
    vare_var.append(checkbox_column.create_checkbox(txt, i))


# Добавляем выбор трех цветов
color_vars1 = tk.StringVar(value="4 0 84")
color_vars2 = tk.StringVar(value="219 222 202")
color_vars3 = tk.StringVar(value="255 0 0")
color_labels = ["Цвет 1", "Цвет 2", "Цвет 3"]
color_vars = [color_vars1, color_vars2, color_vars3]

for i in range(3):
    tk.Label(root, text=color_labels[i]).grid(row=len(params_info) + len(unstable_var) + i, column=0, sticky='w')
    tk.Button(root, text="Выбрать цвет", command=lambda i=i: choose_color(i)).grid(row=len(params_info) + len(unstable_var) + i, column=1)

# Кнопка запуска
tk.Button(root, text="Запустить генерацию", command=generate_mandelbrot).grid(row=len(params_info) + len(unstable_var) + 4, column=0, columnspan=2)
status_label = tk.Label(root, text="")
status_label.grid(row=len(params_info) + len(unstable_var) +  5, column=0, columnspan=2)

root.mainloop()
