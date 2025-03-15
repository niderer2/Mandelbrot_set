import sys
sys.path.insert(0, r'C:\Users\3D МОДЕЛИРОВАНИЕ 8\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages')
from numba import njit
from PIL import Image
import numpy as np

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
                print(f"Введите ровно {count} числа через пробел!")

@njit
def compute_mandelbrot(max_iter, c):
    z = 0 + 0j
    iter_count = 0
    for i in range(max_iter):
        z = z * z + c
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
name = get_values("Введите название картинки. Её тип по умолчанию png: ", str, count=1)
width, height = get_values("Введите размеры картинки через пробел: ", int, count=2)
n_colors, = get_values("Введите градиент картинки (кол-во цветов): ", int, count=1)
max_iter, = get_values("Введите кол-во итераций к каждому пикселю: ", int, count=1)
zoom, = get_values("Введите коэффициент приближения (например, 1 для базового вида, >1 для зума): ", float, count=1)
zoom /= 2
shift_x, shift_y = get_values("Введите сдвиг по х и у через пробел: ", float, count=2)
colors = gradient_colors(n_colors)
mem_img = np.memmap('big_image.dat', dtype=np.uint8, mode='w+', shape=(height, width, 3))
for iy in range(height):
    for ix in range(width):
        x = (ix - width / 2) / (0.5 * zoom * width) - shift_x / 10
        y = (iy - height / 2) / (0.5 * zoom * height) - shift_y / 10
        c = complex(x, y)
        z, iter_count = compute_mandelbrot(max_iter, c)
        if abs(z) <= 2:
            mem_img[iy, ix] = (0, 0, 0)
        else:
            mem_img[iy, ix] = z_index(iter_count % n_colors, colors)
mem_img.flush()
img = Image.fromarray(np.array(mem_img))
img.show()
img.save(f"{name[0]}.png")
