import sys
import os
from numba import njit
import numpy as np
import math
from PIL import Image

def get_values(prompt, cast, count=1):
    while True:
        try:
            parts = input(prompt).split()
            if len(parts) != count:
                raise ValueError
            return [cast(p) for p in parts]
        except ValueError:
            if count == 1:
                print("Введите корректное значение!")
            else:
                print(f"Введите ровно {count} значения через пробел!")

@njit
def compute_mandelbrot(max_iter, c, n1, n2, t1, t2, t3, const, end, sim, if_i, himit1, himit2, himit3):
    z = complex(0.0, 0.0)
    iter_count = 0
    z_i = 0
    for i in range(int(max_iter)):
        if if_i == 'y':
            c_i = (n2 + (i * t2)) * c
            const_i = t3 * const * i
            z = z ** (n1 + (i * t1))
            z = z + c_i + const_i
        else:
            c = (n2 + (i * t2)) * (c ** himit1)
            const = t3 * (const ** himit3) * i
            z_i = n1 + (i * t1) + z_i ** abs(himit2)
            z = z ** z_i
            z = z + c + const           
            
        if sim != 0:
            z = z * math.sin(abs(z)) * sim
        if abs(z) > end:
            iter_count = i
            break
    else:
        iter_count = max_iter
    return z, iter_count

def gradient_colors(n, color_1, color_2, color_3):
    cr_1 = 1.0  # длина перехода от color_1 к color_2
    cr_2 = 1.0  # длина плато, где цвет равен color_2
    cr_3 = 1.0  # длина перехода от color_2 к color_3 (больше пространства)
    
    total = cr_1 + cr_2 + cr_3
    
    if n == 1:
        return [color_1]
    
    gradient = []
    for i in range(n):
        # Нормализуем позицию от 0 до 1
        t = i / (n - 1)
        
        # Определяем, в каком сегменте мы находимся
        if t <= cr_1 / total:
            # Первая часть: интерполяция от color_1 до color_2
            local_ratio = t / (cr_1 / total)
            color = [
                int(color_1[j] + local_ratio * (color_2[j] - color_1[j]))
                for j in range(3)
            ]
        elif t <= (cr_1 + cr_2) / total:
            # Плато: цвет равен color_2
            color = color_2.copy()
        else:
            # Третья часть: интерполяция от color_2 до color_3
            local_t = (t - (cr_1 + cr_2) / total) / (cr_3 / total)
            color = [
                int(color_2[j] + local_t * (color_3[j] - color_2[j]))
                for j in range(3)
            ]
        gradient.append(color)
    
    return gradient

def z_index(z, colors):
    if z < len(colors):
        return colors[z]
    else:
        return colors[-1]
#print(gradient_colors(10, [0, 0, 255], [200, 200, 255], [255, 0, 0]))
print('пропустите этот ввод')
if input() != 'tyjknbvcdfghnbvfrgthkg,vmmn':
    a = "Введите название картинки. Её тип по умолчанию png: "
    a1 = "Введите размеры картинки через пробел: "
    a2 = "Введите градиент картинки (кол-во цветов): "
    w1 = 'цвет 1, укажите 3 числа через пробел RGB: '
    w2 = 'цвет 2, укажите 3 числа через пробел RGB: '
    w3 = 'цвет 3, укажите 3 числа через пробел RGB: '
    a3 = "Введите множители для степени и для точки (стандарт: 2 1): "
    a4 = "Введите прибавляемую константу(стандарт: 0): "
    a5 = "Введите множитель к номеру итерации к степени, значению, константе (стандарт: 0 0 0): "
    a5_1 = "Введите множитель к синусу (0 его убирает. Стандарт: 0) : "
    a6 = "Введите границы множества (стандарт: 2): "
    a7 = "Введите макс кол-во итераций: "
    a8 = "Введите коэффициент приближения (например, 1 для базового вида, >1 для зума): "
    a9 = "Введите сдвиг по х и у через пробел: "
    a10 = 'Использовать нестабильный оператор? y/n: '
    a11 = 'Степень для нестабильного оператора, степени, множителя, константы'
else:
    a, a1, a2, a3, a4, a5, a5_1, a6, a7, a8, a9, a10, a11, w1, w2, w3 = '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
    
name = get_values(a, str, count=1) 
width, height = get_values(a1, int, count=2)
n_colors, = get_values(a2, int, count=1)
color_1 = get_values(w1, int, count=3)
color_2 = get_values(w2, int, count=3)
color_3 = get_values(w3, int, count=3)
n1, n2 = get_values(a3, float, count=2)
const, = get_values(a4, float, count=1)
t1, t2, t3 = get_values(a5, float, count=3)
sim, = get_values(a5_1, float, count=1)
end, = get_values(a6, float, count=1)
max_iter, = get_values(a7, int, count=1)
zoom, = get_values(a8, float, count=1)
shift_x, shift_y = get_values(a9, float, count=2)
if_i = get_values(a10, str, count=1)
himit1, himit2, himit3 = get_values(a11, float, count=3)

colors = gradient_colors(n_colors, color_1, color_2, color_3)

zoom = zoom / 2
try:
    mem_img = np.memmap('big_image.dat', dtype=np.uint8, mode='w+', shape=(height, width, 3))
except OSError as e:
    print("Ошибка при создании файла memmap. Вероятно, недостаточно места на диске.")
    print(e)
    exit()
last_printed = -1
for iy in range(height):
    progress = int((iy + 1) / height * 100)
    if width <= 1000 and height <= 1000:
        if progress in (0, 25, 50, 75, 100) and progress != last_printed:
            print(f"{progress}% завершено")
            last_printed = progress
    else:
        if progress != last_printed:
            print(f"{progress}% завершено")
            last_printed = progress
    for ix in range(width):
        x = (ix - width / 2) / (0.5 * zoom * width) - shift_x / 10
        y = (iy - height / 2) / (0.5 * zoom * height) - shift_y / 10
        c = complex(x, y)
        z, iter_count = compute_mandelbrot(max_iter, c, n1, n2, t1, t2, t3, const, end, sim, if_i, himit1, himit2, himit3)
        if abs(z) <= end:
            mem_img[iy, ix] = (0, 0, 0)
        else:
            mem_img[iy, ix] = z_index(iter_count % len(colors), colors)

mem_img.flush()
img = Image.fromarray(np.array(mem_img))
img.show()
directory = "images"
if not os.path.exists(directory):
    os.makedirs(directory)
img.save(os.path.join(directory, f"{name[0]}.png"))
print("Изображение успешно сохранено.")
print('')