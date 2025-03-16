import sys
import os
from numba import njit
import numpy as np
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
def compute_mandelbrot(max_iter, c, n1, n2, t1, t2):
    z = 0 + 0j
    iter_count = 0
    for i in range(max_iter):
        # Формула изменяется в зависимости от номера итерации
        z = z ** (n1 + (i * t1)) + (n2 + (i * t2)) * c
        if abs(z) > 2:
            iter_count = i
            break
    else:
        iter_count = max_iter
    return z, iter_count

def gradient_colors(n):
    colors = []
    start = (173, 216, 230)  # бледно-синий
    end = (255, 0, 0)        # красный
    steps = 2 * n
    for i in range(steps):
        t = i / (steps - 1)
        r = int(start[0] + t * (end[0] - start[0]))
        g = int(start[1] + t * (end[1] - start[1]))
        b = int(start[2] + t * (end[2] - start[2]))
        colors.append((r, g, b))
    return colors

def z_index(z, colors):
    if z < len(colors):
        return colors[z]
    else:
        return colors[-1]

# Получаем параметры от пользователя
name = get_values("Введите название картинки. Её тип по умолчанию png: ", str, count=1)
width, height = get_values("Введите размеры картинки через пробел: ", int, count=2)
n_colors, = get_values("Введите градиент картинки (кол-во цветов): ", int, count=1)
n1, n2 = get_values("Введите множители для степени и для точки (стандарт: 2 1): ", float, count=2)
t1, t2 = get_values("Введите множитель к номеру цикла к степени и значению (стандарт: 0 0): ", int, count=2)
max_iter, = get_values("Введите кол-во итераций к каждому пикселю: ", int, count=1)
zoom, = get_values("Введите коэффициент приближения (например, 1 для базового вида, >1 для зума): ", float, count=1)
zoom /= 2
shift_x, shift_y = get_values("Введите сдвиг по х и у через пробел: ", float, count=2)
colors = gradient_colors(n_colors)

# Расчёт требуемого места:
# На изображение RGB требуется width*height*3 байт.
# При генерации используется в 2 раза больше места.
required_bytes = width * height * 3 * 2  
if required_bytes < 10**9:
    required_space = required_bytes / (1024 * 1024)  # в МБ
    space_str = f"{required_space:.2f} МБ"
else:
    required_space = required_bytes / (1024 * 1024 * 1024)  # в ГБ
    space_str = f"{required_space:.2f} ГБ"

print(f"Внимание: генерация данной картинки потребует примерно {space_str} дискового пространства.")
ans = input("Уверены, что хотите продолжить? (y/n): ").strip().lower()
if ans != 'y':
    print("Операция отменена пользователем.")
    exit()

# Пытаемся создать memmap в блоке try/except
try:
    mem_img = np.memmap('big_image.dat', dtype=np.uint8, mode='w+', shape=(height, width, 3))
except OSError as e:
    print("Ошибка при создании файла memmap. Вероятно, недостаточно места на диске.")
    print(e)
    exit()

# Вычисление изображения с выводом шкалы прогресса
last_printed = -1
for iy in range(height):
    # Рассчитываем прогресс в процентах (целое число)
    progress = int((iy + 1) / height * 100)
    if width <= 1000 and height <= 1000:
        # Выводим только 0%, 25%, 50%, 75% и 100%
        if progress in (0, 25, 50, 75, 100) and progress != last_printed:
            print(f"{progress}% завершено")
            last_printed = progress
    else:
        # Выводим сообщение при каждом изменении процента
        if progress != last_printed:
            print(f"{progress}% завершено")
            last_printed = progress
    for ix in range(width):
        x = (ix - width / 2) / (0.5 * zoom * width) - shift_x / 10
        y = (iy - height / 2) / (0.5 * zoom * height) - shift_y / 10
        c = complex(x, y)
        z, iter_count = compute_mandelbrot(max_iter, c, n1, n2, t1, t2)
        if abs(z) <= 2:
            mem_img[iy, ix] = (0, 0, 0)
        else:
            mem_img[iy, ix] = z_index(iter_count % n_colors, colors)

mem_img.flush()

# Преобразуем memmap в обычный массив и создаём изображение PIL
img = Image.fromarray(np.array(mem_img))
img.show()
img.save(f"{name[0]}.png")
print("Изображение успешно сохранено.")

# Удаляем временный файл с данными
try:
    os.remove('big_image.dat')
    print("Временный файл удалён.")
except Exception as e:
    print("Не удалось удалить временный файл:")
    print(e)
