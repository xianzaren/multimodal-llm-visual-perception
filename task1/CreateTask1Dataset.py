import numpy as np
import openpyxl
from openpyxl.styles import PatternFill
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
from scipy.fftpack import fft2, fftshift
import os

def save_colorbar_rgb(cmap, tick_positions, save_path):
    # 如果 cmap 是字符串，转换为 Colormap 对象
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    with open(save_path, 'w') as f:
        f.write("Tick Value, R, G, B\n")  # 写入表头
        for tick in tick_positions:
            # 将刻度值归一化到 [0, 1] 范围
            normalized_value = tick / 1000.0
            # 获取对应的 RGB 值
            rgb = cmap(normalized_value)[:3]  # 只取前三个值 (R, G, B)
            # 将 RGB 值写入文件
            f.write(f"{tick:.0f}, {rgb[0]:.6f}, {rgb[1]:.6f}, {rgb[2]:.6f}\n")

# 1) 生成 Perlin 噪声的函数
def generate_seamless_perlin_noise_2d(shape, res, octaves=5, persistence=0.5, seed=42):
    def f(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    def gradient_grid(res):
        np.random.seed(seed)  # 如需固定随机种子，可取消注释
        angles = 2 * np.pi * np.random.rand(res[0], res[1])
        gradients = np.dstack((np.cos(angles), np.sin(angles))).astype(np.float64)
        return gradients

    def perlin(x, y, gradients):
        x0 = np.floor(x).astype(np.int64) % gradients.shape[0]
        y0 = np.floor(y).astype(np.int64) % gradients.shape[1]
        x1 = (x0 + 1) % gradients.shape[0]
        y1 = (y0 + 1) % gradients.shape[1]

        dx = x - x0.astype(np.float64)
        dy = y - y0.astype(np.float64)

        sx = f(dx)
        sy = f(dy)

        g00 = gradients[x0, y0]
        g10 = gradients[x1, y0]
        g01 = gradients[x0, y1]
        g11 = gradients[x1, y1]

        n00 = g00[..., 0] * dx + g00[..., 1] * dy
        n10 = g10[..., 0] * (dx - 1) + g10[..., 1] * dy
        n01 = g01[..., 0] * dx + g01[..., 1] * (dy - 1)
        n11 = g11[..., 0] * (dx - 1) + g11[..., 1] * (dy - 1)

        nx0 = (1 - sx) * n00 + sx * n10
        nx1 = (1 - sx) * n01 + sx * n11
        return (1 - sy) * nx0 + sy * nx1

    noise = np.zeros(shape, dtype=np.float64)

    # 修正 max_amplitude 计算
    max_amplitude = (1 - persistence ** octaves) / (1 - persistence)

    frequency = 1
    amplitude = 1

    for _ in range(octaves):
        res_x, res_y = int(res[0] * frequency), int(res[1] * frequency)
        gradients = gradient_grid((res_x, res_y))

        delta = (res_x / shape[0], res_y / shape[1])
        grid_x, grid_y = np.meshgrid(
            np.arange(0, shape[1]) * delta[1],
            np.arange(0, shape[0]) * delta[0]
        )

        noise += amplitude * perlin(grid_x, grid_y, gradients)
        amplitude *= persistence
        frequency *= 2

    print("原始噪声范围: {:.20f} ~ {:.20f}".format(noise.min(), noise.max()))
    normalized_noise = noise / max_amplitude
    min_value = normalized_noise.min()
    max_value = normalized_noise.max()

    # 归一化到 [0, 1]
    normalized_noise = (normalized_noise - min_value) / (max_value - min_value)
    # 放大到 [0, 1000] 并取整
    normalized_noise = np.rint(normalized_noise * 1000).astype(int)
    normalized_noise = np.clip(normalized_noise, 0, 1000)
    print("最终最大值: {} 最终最小值: {}".format(normalized_noise.max(), normalized_noise.min()))

    return normalized_noise

# 2) 计算功率谱（可选）
def compute_power_spectrum(noise):
    fft_values = fftshift(fft2(noise))
    magnitude = np.abs(fft_values)
    power_spectrum = np.log1p(magnitude ** 2)
    return power_spectrum

# 4) 生成不带坐标轴的纯粹标量场图
def plot_scalar_field(shape, noise, colormap, filepath):
    dpi = 100
    figsize_width = shape[1] / dpi + 1e-9
    figsize_height = shape[0] / dpi + 1e-9

    plt.figure(figsize=(figsize_width, figsize_height), dpi=dpi)
    plt.imshow(noise, cmap=colormap, origin='upper', vmin=0, vmax=1000)
    plt.axis('off')
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, left=0, right=1, hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.savefig(filepath, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()

def create_blueyellow_colormap():
    blue = (13/255.0, 0/255.0, 252/255.0)
    yellow = (252/255.0, 252/255.0, 0/255.0)
    return mcolors.LinearSegmentedColormap.from_list("blueyellow", [blue, yellow], N=256)

'''def create_blackpurple_redyellow_white_colormap():
    # 定义黑色、紫色、红色、黄色和白色的 RGB 值
    color1 = (0 / 255.0, 0 / 255.0, 0 / 255.0)
    color2 = (26 / 255.0, 19 / 255.0, 92 / 255.0)
    color3 = (36 / 255.0, 22 / 255.0, 180 / 255.0)
    color4 = (145 / 255.0, 0 / 255.0, 193 / 255.0)
    color5 = (226 / 255.0, 45 / 255.0, 60 / 255.0)
    color6 = (251 / 255.0, 108 / 255.0, 57 / 255.0)
    color7 = (249 / 255.0, 167 / 255.0, 44 / 255.0)
    color8 = (246 / 255.0, 219 / 255.0, 92 / 255.0)
    color9 = (255 / 255.0, 255 / 255.0, 255 / 255.0)
    # 创建并返回自定义 colormap
    return mcolors.LinearSegmentedColormap.from_list("blackpurple_redyellow_white", [color1, color2, color3, color4, color5, color6, color7, color8, color9],
                                                     N=256)'''

def main():
    # 目标图像大小 (630, 820)
    shape = (630, 820)
    octaves = 5
    # 尝试不同的分辨率组合
    res_list = [(1, 1), (3, 3), (5, 5), (7, 7), (9, 9)]

    # 定义自定义色图
    blueyellow_name = "blueyellow"
    blueyellow = create_blueyellow_colormap()

    # Matplotlib 自带的色图 + 自定义色图
    colormap_list = [
        'gray', 'Blues', 'hot', 'cubehelix', 'magma',
        'coolwarm', 'rainbow', 'spectral', blueyellow_name
    ]

    # 目录结构（根据需要修改）
    uncolor_dir = r'../../data/uncolor'
    colored_dir = r'../../data/colored'
    dir_folder = 'exp1'
    image_dir_map = {
        'gray': fr'../../color/{dir_folder}/gray',
        'rainbow': fr'../../color/{dir_folder}/rainbow',
        'hot': fr'../../color/{dir_folder}/hot',
        'Blues': fr'../../color/{dir_folder}/Blues',
        'cubehelix': fr'../../color/{dir_folder}/cubehelix',
        'magma': fr'../../color/{dir_folder}/magma',
        'coolwarm': fr'../../color/{dir_folder}/coolwarm',
        'spectral': fr'../../color/{dir_folder}/spectral',
        'blueyellow': fr'../../color/{dir_folder}/blueyellow'
    }

    os.makedirs(uncolor_dir, exist_ok=True)
    os.makedirs(colored_dir, exist_ok=True)
    for cdir in image_dir_map.values():
        os.makedirs(cdir, exist_ok=True)

    for res in res_list:
        print(f"\n生成 Perlin 噪声: shape={shape}, res={res}, octaves={octaves}")
        noise = generate_seamless_perlin_noise_2d(shape, res, octaves, seed=42)
        print("最大值:", noise.max(), "最小值:", noise.min())

        # 先保存到 txt 和 csv
        csv_filename = f"Noise_{shape}_{res}_{octaves}.csv"
        txt_filename = f"Noise_{shape}_{res}_{octaves}.txt"
        csv_filepath = os.path.join(uncolor_dir, csv_filename)
        txt_filepath = os.path.join(uncolor_dir, txt_filename)

        np.savetxt(txt_filepath, noise.astype(np.float64), fmt="%.16f")
        print(f"TXT 文件已保存: {txt_filepath}")

        data = np.loadtxt(txt_filepath)
        np.savetxt(csv_filepath, data, delimiter=",", fmt="%.16f",
                   header="Normalized Elevation Data", comments="")
        print(f"CSV 文件已保存: {csv_filepath}")

        # 针对不同色图绘制
        for cm in colormap_list:
            if cm == 'Blues':
                cmap = 'Blues_r'
            elif cm == 'spectral':
                cmap = 'nipy_spectral'
            elif cm == blueyellow_name:
                cmap = blueyellow
            else:
                cmap = cm

            # 1) 先绘制带 colorbar 的图
            colorbar_png_name = f"Colorbar_{cm}_{shape}_{res}_{octaves}.png"
            colorbar_png_path = os.path.join(image_dir_map[cm], colorbar_png_name)

            dpi = 100
            figsize_height = shape[0] / dpi  # 630 / 100 = 6.3 inches
            figsize_width = 767 / dpi        # 原先的设置
            fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
            cax = ax.imshow(noise, cmap=cmap, origin='upper', vmin=0, vmax=1000)
            cbar = plt.colorbar(cax, label='Elevation', fraction=0.030, pad=0.05)
            # 生成 9 个刻度，覆盖 [0, 1000]
            tick_positions = np.linspace(0, 1000, 9)
            cbar.set_ticks(tick_positions)
            cbar.set_ticklabels([f"{t:.0f}" for t in tick_positions])

            plt.axis('off')
            plt.savefig(colorbar_png_path, dpi=150, bbox_inches='tight', pad_inches=0)
            plt.close()

            colorbar_rgb_txt_name = f"Colorbar_RGB_{cm}_{shape}_{res}_{octaves}.txt"
            colorbar_rgb_txt_path = os.path.join(image_dir_map[cm], colorbar_rgb_txt_name)
            save_colorbar_rgb(cmap, tick_positions, colorbar_rgb_txt_path)

            # 2) 保存纯标量场图（无 colorbar）
            scalar_field_dir = os.path.join(image_dir_map[cm], "exps")
            os.makedirs(scalar_field_dir, exist_ok=True)
            scalar_field_png_name = f"ScalarField_{cm}_{shape}_{res}_{octaves}.png"
            scalar_field_png_path = os.path.join(scalar_field_dir, scalar_field_png_name)
            plot_scalar_field(shape, noise, cmap, scalar_field_png_path)

            # 验证 CSV 文件内容
            loaded_noise = np.loadtxt(csv_filepath, delimiter=",", skiprows=1)
            print("CSV 加载后最大值: {:.20f}".format(loaded_noise.max()))
            print("CSV 加载后最小值: {:.20f}".format(loaded_noise.min()))

if __name__ == "__main__":
    main()
