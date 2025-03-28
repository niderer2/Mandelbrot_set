import sys
import os
import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
from numba import njit, vectorize, prange
import numpy as np
import math
import cmath
from PIL import Image
from tqdm import tqdm


@njit
def safe_abs(n):
    real_abs = abs(n.real)
    imag_abs = abs(n.imag)
    s = max(real_abs, imag_abs)
    if s == 0:
        return 0
    return s * math.sqrt((real_abs / s) ** 2 + (imag_abs / s) ** 2)

@njit
def custom_pow(z, n, if_rotate):
    if n.imag != 0 and if_rotate == '1':
        return cmath.exp(-n.imag * cmath.phase(z))
    else:
        if z != complex(0.0, 0.0):
            return z ** n
        else:
            return 0
        
@njit
def factor_(c, n, if_factor, if_zoom):
    if if_factor == '1':
        c = c * n.real * complex(0, n.imag)
    else:
        c = c * n
    
    if if_zoom == '1':
        if if_factor == '1':
            c = c / (n.real ** 2 + n.imag ** 2) ** 0.5
    return c
            

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
def compute_mandelbrot(max_iter, c, n1, n2, t1, t2, t3, const, end, if_i, himit1, himit2, himit3, sim_degree, sim_factor, sim_sum, cos_degree, cos_factor, cos_sum, if_mod_1, if_mod_2, if_mod_3, if_mod_4, if_mod_x_z, if_mod_y_z, if_mod_x_c, if_mod_y_c, if_rotate, if_zoom, if_factor, if_radian, if_zc):
    z = complex(0.0, 0.0)
    iter_count = 0
    z_i = complex(0.0, 0.0)
    if if_mod_4 == '1':
        c = complex(safe_abs(c), 0) 
    for i in range(int(max_iter)):        
        c_new = c
        if if_mod_3 == '1':
            z = complex(safe_abs(z))      
        
        if if_mod_x_c == '1':
            c_new = complex(safe_abs(c_new.real), c_new.imag)
        if if_mod_y_c == '1':
            c_new = complex(c_new.real, safe_abs(c_new.imag))         
        
        
        if if_i == '0':
            c_i = factor_(c_new, n2 + (i * t2), if_factor, if_zoom)
            const_i = const * t3 * i + const
            kilim = n1 + i * t1
            z = custom_pow(z, kilim, if_rotate)
            z = z + c_i + const_i
        else:
            c_r, c_n = custom_pow(c_new, himit1, if_rotate), n2 + (i * t2)
            c_new = factor_(c_r, c_n, if_factor, if_zoom)
            const = custom_pow(const, himit3, if_rotate) * i * t3 + const
            z_i = n1 + i * t1 + custom_pow(z_i, himit2, if_rotate)
            z = custom_pow(z, z_i, if_rotate)
            z = z + c_new + const           
        
        
        if if_zc == '0':
            ki = z
        else:
            ki = c
            
        if if_radian == '1':
            ki = safe_abs(ki)
        if sim_factor != 0:
            if if_mod_2 == '1':
                u = safe_abs(cmath.sin(ki))
            else:
                u = cmath.sin(ki)
            z = z * custom_pow(u, sim_degree, if_rotate) * sim_factor
        if cos_factor != 0:
            if if_mod_2 == '1':
                u = safe_abs(cmath.cos(ki))
            else:
                u = cmath.cos(ki)           
            z = z * custom_pow(u, cos_degree, if_rotate) * cos_factor
        if if_mod_2 == '1':
            z = z + safe_abs(cmath.sin(ki)) * sim_sum + safe_abs(cmath.cos(ki)) * cos_sum
        else:
            z = z + cmath.sin(ki) * sim_sum + cmath.cos(ki) * cos_sum
        
        if if_mod_x_z == '1':
            z = complex(safe_abs(z.real), z.imag)
        if if_mod_y_z == '1':
            z = complex(z.real, safe_abs(z.imag))
        
        if if_mod_1 == '1':
            z = complex(safe_abs(z), 0)
        
        if safe_abs(z) > end or math.isnan(safe_abs(z)):
            iter_count = i
            break
    else:
        iter_count = max_iter
    return z, iter_count


def gradient_colors(n, color_1, color_2, color_3, cr_1, cr_2, cr_3):
    total = cr_1 + cr_2 + cr_3
    
    if n == 1:
        return [color_1]
    
    gradient = []
    for i in range(n):
        t = i / (n - 1)
        if t <= cr_1 / total:
            local_ratio = t / (cr_1 / total)
            color = [
                int(color_1[j] + local_ratio * (color_2[j] - color_1[j]))
                for j in range(3)
            ]
        elif t <= (cr_1 + cr_2) / total:
            color = color_2.copy()
        else:
            local_t = (t - (cr_1 + cr_2) / total) / (cr_3 / total)
            color = [
                int(color_2[j] + local_t * (color_3[j] - color_2[j]))
                for j in range(3)
            ]
        gradient.append(color)
    
    return gradient

@njit
def z_index(z, colors_len):
    if math.isnan(z):
        return 0
    elif z < colors_len:
        return int(z)
    else:
        return -1

@njit
def z_color(iter_count, max_iteret, colors_len, if_log, zet, endet):
    if if_log == '1':
        alpha = math.log(1 + iter_count) / max_iteret * endet * zet
        index = alpha * (colors_len - 1)
        return z_index(index % colors_len, colors_len)        
    else:
        return z_index(iter_count % colors_len, colors_len)

name, = get_values('', str, count=1) 
width, height = get_values('', int, count=2)
n_colors, = get_values('', int, count=1)
color_1 = get_values('', int, count=3)
color_2 = get_values('', int, count=3)
color_3 = get_values('', int, count=3)
n1_n, n1_i, n2_n, n2_i = get_values('', float, count=4)
n1, n2 = complex(n1_n, n1_i), complex(n2_n, n2_i)
const_n, const_i = get_values('', float, count=2)
const = complex(const_n, const_i)
t1_n, t1_i, t2_n, t2_i, t3_n, t3_i = get_values('', float, count=6)
t1, t2, t3 = complex(t1_n, t1_i), complex(t2_n, t2_i), complex(t3_n, t3_i)
sim_degree_n, sim_degree_i, sim_factor_n, sim_factor_i, sim_sum_n, sim_sum_i = get_values('', float, count=6)
sim_degree, sim_factor, sim_sum = complex(sim_degree_n, sim_degree_i), complex(sim_factor_n, sim_factor_i), complex(sim_sum_n, sim_sum_i)
cos_degree_n, cos_degree_i, cos_factor_n, cos_factor_i, cos_sum_n, cos_sum_i = get_values('', float, count=6)
cos_degree, cos_factor, cos_sum = complex(cos_degree_n, cos_degree_i), complex(cos_factor_n, cos_factor_i), complex(cos_sum_n, cos_sum_i)
end, = get_values('', float, count=1)
max_iter, = get_values('', int, count=1)
zoom, = get_values('', float, count=1)
shift_x, shift_y = get_values('', float, count=2)
if_i, = get_values('', str, count=1)
himit1_n, himit1_i, himit2_n, himit2_i, himit3_n, himit3_i = get_values('', float, count=6)
himit1, himit2, himit3 = complex(himit1_n, himit1_i), complex(himit2_n, himit2_i), complex(himit3_n, himit3_i)
if_mod_1, if_mod_2, if_mod_3, if_mod_4 = get_values('', str, count=4)
if_mod_x_z, if_mod_y_z = get_values('', str, count=2)
if_mod_x_c, if_mod_y_c = get_values('', str, count=2)
if_radian, if_zc = get_values('', str, count=2)
if_rotate, = get_values('', str, count=1)
if_zoom, = get_values('', str, count=1)
if_factor, = get_values('', str, count=1)
if_log, = get_values('', str, count=1)
values_endet, values_zet = get_values('', float, count=2)

cr_1, cr_2, cr_3 = 1.0, 1.0, 1.0
colors = gradient_colors(n_colors, color_1, color_2, color_3, cr_1, cr_2, cr_3)

zoom = zoom / 2
#print(if_log, if_log == '1')

endet = math.log(1 + end) ** values_endet  
max_iteret = math.log(1 + max_iter)

plt.ion()
fig, ax = plt.subplots()
ax.axis('off')

display_width = 1000 if width > 1000 else width
display_height = 1000 if height > 1000 else height
display_data = np.zeros((display_height, display_width, 3), dtype=np.uint8)
im_handle = ax.imshow(display_data)
plt.title("Процесс построения изображения")

try:
    mem_img = np.memmap('big_image.dat', dtype=np.uint8, mode='w+', shape=(height, width, 3))
except OSError as e:
    print("Ошибка при создании файла memmap. Вероятно, недостаточно места на диске.")
    print(e)
    exit()
    
last_printed = -1
colors = np.array(colors, dtype=np.uint8)
@njit(parallel=True)
def compute_fractal(width, height, zoom, shift_x, shift_y,
                    max_iter, n1, n2, t1, t2, t3, const, end, if_i, 
                    himit1, himit2, himit3, sim_degree, sim_factor, sim_sum, 
                    cos_degree, cos_factor, cos_sum, if_mod_1, if_mod_2, if_mod_3, if_mod_4, 
                    if_mod_x_z, if_mod_y_z, if_mod_x_c, if_mod_y_c, if_rotate, if_zoom, 
                    if_factor, if_radian, if_zc, max_iteret, colors, if_log, values_zet, endet, iy):
    w = np.zeros((width, 3), dtype=np.uint8)
    for ix in prange(width):
        # Пересчёт координат для текущей точки
        x = (ix - width / 2) / (0.5 * zoom * width) - shift_x / 10
        y = (iy - height / 2) / (0.5 * zoom * height) - shift_y / 10
        c = complex(x, y)
            
        # Вычисление мандельброта для точки
        z, iter_count = compute_mandelbrot(max_iter, c, n1, n2, t1, t2, t3, 
                                                 const, end, if_i, himit1, himit2, himit3, 
                                                 sim_degree, sim_factor, sim_sum, 
                                                 cos_degree, cos_factor, cos_sum, 
                                                 if_mod_1, if_mod_2, if_mod_3, if_mod_4, 
                                                 if_mod_x_z, if_mod_y_z, if_mod_x_c, if_mod_y_c, 
                                                 if_rotate, if_zoom, if_factor, if_radian, if_zc)
        # Раскрашиваем точки
        if safe_abs(z) <= end:
            w[ix] = (0, 0, 0)
        else:

            w[ix] = colors[z_color(iter_count, max_iteret, len(colors), if_log,
                                          math.log(1 + safe_abs(z)) ** values_zet, endet)]
    return w


@njit(parallel=True)
def prisw(mem_img, w, iy, width):
    for ix in prange(width):
        mem_img[iy, ix] = w[ix]
    return mem_img

for iy in tqdm(range(height)):
    w = compute_fractal(
        width, height, zoom, shift_x, shift_y,
        max_iter, n1, n2, t1, t2, t3, const, end, if_i, 
        himit1, himit2, himit3, sim_degree, sim_factor, sim_sum, 
        cos_degree, cos_factor, cos_sum, if_mod_1, if_mod_2, if_mod_3, if_mod_4, 
        if_mod_x_z, if_mod_y_z, if_mod_x_c, if_mod_y_c, if_rotate, if_zoom, 
        if_factor, if_radian, if_zc, max_iteret, colors, if_log, values_zet, endet, iy)
    mem_img = prisw(mem_img, w, iy, width)
    if width > 1000 or height > 1000:
        full_img = Image.fromarray(np.array(mem_img))
        display_img = full_img.resize((display_width, display_height), Image.ANTIALIAS)
        display_data = np.array(display_img)
    else:
        display_data = np.array(mem_img)
        
    im_handle.set_data(display_data)
    fig.canvas.draw_idle()
    plt.pause(0.001)

plt.close(fig)
mem_img.flush()
img = Image.fromarray(np.array(mem_img))
img.show()
directory = "images"
if not os.path.exists(directory):
    os.makedirs(directory)
img.save(os.path.join(directory, f"{name}.png"))

with open(f"images/{name}_info.txt", "w", encoding="utf-8") as file:
    file.write(f'''
Осторожно файл "Множество Мондельброта.py" принимает не такими "Интерфейс.py"

Параметры:
{name}
{width} {height}
{n_colors}
{color_1[0]} {color_1[1]} {color_1[2]}
{color_2[0]} {color_2[1]} {color_2[2]}
{color_3[0]} {color_3[1]} {color_3[2]}
{n1_n} {n1_i} {n2_n} {n2_i}
{const_n}, {const_i}
{t1_n} {t1_i} {t2_n} {t2_i} {t3_n} {t3_i}
{sim_degree_n} {sim_degree_i} {sim_factor_n} {sim_factor_i} {sim_sum_n} {sim_sum_i}
{cos_degree_n} {cos_degree_i} {cos_factor_n} {cos_factor_i} {cos_sum_n} {cos_sum_i}
{end}
{max_iter}
{zoom}
{shift_x}, {shift_y}
{if_i}
{himit1_n} {himit1_i} {himit2_n} {himit2_i} {himit3_n} {himit3_i}
{if_mod_1} {if_mod_2} {if_mod_3} {if_mod_4}
{if_mod_x_z} {if_mod_y_z}
{if_mod_x_c} {if_mod_y_c}
{if_radian} {if_zc}
{if_rotate}
{if_zoom}
{if_factor}
{if_log}
{values_endet} {values_zet}
    ''')
print("Изображение успешно сохранено.")
for i in range(3):
    print('')