import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import os
import random
from PIL import Image
import matplotlib.colors as mcolors

# 定义 blueyellow colormap
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


# 计算方框内的梯度平均值
def compute_gradient_average(box):
    gradient_x, gradient_y = np.gradient(box)
    gradient_magnitude = np.sqrt(gradient_x ** 2 + gradient_y ** 2)
    return np.mean(gradient_magnitude)


# 在图像中寻找满足比率条件的方框
def find_matching_box(noise, x1, y1, target_ratio, tolerance, box_size=175, max_iterations=50000):
    height, width = noise.shape
    iterations = 0  # 记录迭代次数

    while True:
        x2 = random.randint(30, width - box_size - 30)
        y2 = random.randint(30, height - box_size - 30)
        iterations += 1

        # 确保不重叠
        if abs(x1 - x2) > box_size or abs(y1 - y2) > box_size:
            box1 = noise[y1:y1 + box_size, x1:x1 + box_size]
            box2 = noise[y2:y2 + box_size, x2:x2 + box_size]
            avg1 = compute_gradient_average(box1)
            avg2 = compute_gradient_average(box2)
            flatter, steeper = sorted([avg1, avg2])  # 确保 flatter <= steeper
            ratio = flatter / steeper if steeper != 0 else 0
            # 检查是否满足当前容忍度
            if abs(ratio - target_ratio) <= tolerance:
                return x2, y2, avg1, avg2

        # 动态调整容忍度
        if iterations % max_iterations == 0:
            tolerance += 0.01
            print(f"⚠️ 迭代次数达到 {iterations}，容忍度增加至: {tolerance:.2f}")
        if iterations > 500000:
            print("❌ 达到最大迭代次数，放弃搜索")
            return None


# 根据 colormap 返回框的颜色和文本描述
def get_box_colors(colormap):
    # 如果 colormap 为字符串，则直接使用；否则尝试获取 name 属性
    if isinstance(colormap, str):
        cmap_str = colormap
    elif hasattr(colormap, 'name'):
        cmap_str = colormap.name
    else:
        cmap_str = ""
    if cmap_str == "hot":
        return ('purple', 'green', "Purple Box Avg", "Green Box Avg")
    elif cmap_str == "rainbow":
        return ('black', 'white', "Black Box Avg", "White Box Avg")
    elif cmap_str == "gray":
        return ('red', 'blue', "Red Box Avg", "Blue Box Avg")
    elif cmap_str == "Blues_r":
        return ('yellow', 'green', "Yellow Box Avg", "Green Box Avg")
    elif cmap_str == "coolwarm":
        return ('purple', 'green', "Purple Box Avg", "Green Box Avg")
    elif cmap_str == "cubehelix":
        return ('red', 'blue', "Red Box Avg", "Blue Box Avg")
    elif cmap_str == "magma":
        return ('green', 'blue', "Green Box Avg", "Blue Box Avg")
    elif cmap_str == "nipy_spectral":
        return ('black', 'white', "Black Box Avg", "White Box Avg")
    elif cmap_str == "blueyellow":
        return ('Purple', 'Green', "Purple Box Avg", "Green Box Avg")
    else:
        return ('red', 'blue', "Red Box Avg", "Blue Box Avg")


# 生成图像并绘制方框，同时采用自定义的 colorbar 处理方式
def generate_image_with_boxes_and_compare(noise, colormap, output_filepath, result_filepath, target_ratios,
                                          tolerance=0.05):
    height, width = noise.shape
    box_size = 175
    random.seed(42)  # 确保实验可重复性

    # 获取框颜色和文本描述
    first_color_default, second_color_default, first_text_default, second_text_default = get_box_colors(colormap)

    with open(result_filepath, "a") as result_file:
        for i, target_ratio in enumerate(target_ratios):
            while True:
                first_is_red = random.choice([True, False])
                # 根据随机结果，交换左右框的颜色和文本
                if first_is_red:
                    first_color, second_color = first_color_default, second_color_default
                    first_text, second_text = first_text_default, second_text_default
                else:
                    first_color, second_color = second_color_default, first_color_default
                    first_text, second_text = second_text_default, first_text_default

                # 随机生成第一个方框位置
                x1 = random.randint(30, width - box_size - 30)
                y1 = random.randint(30, height - box_size - 30)

                # 寻找满足比率条件的第二个方框
                match = find_matching_box(noise, x1, y1, target_ratio, tolerance, box_size)
                if match:
                    x2, y2, avg1, avg2 = match
                    flatter, steeper = sorted([avg1, avg2])
                    ratio = flatter / steeper if steeper != 0 else 0
                    print(f"[Colormap: {colormap}] Image {i + 1}:")
                    print(
                        f"  {first_text}: {avg1:.4f}, {second_text}: {avg2:.4f}, Ratio: {ratio:.4f} (Target: {target_ratio})")

                    # 将结果写入文件
                    steeper_text = first_text if avg1 > avg2 else second_text

                    # 根据 noise 大小和 dpi 设置 Figure 尺寸
                    dpi = 100
                    figsize_width = 767 / dpi
                    figsize_height = 630 / dpi
                    fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
                    # 使用指定的数据范围 [0,1000]
                    im = ax.imshow(noise, cmap=colormap, origin='upper', vmin=0, vmax=1000)
                    # 按照指定方式生成 colorbar
                    cbar = plt.colorbar(im, label='Elevation', fraction=0.030, pad=0.05)
                    tick_positions = np.linspace(0, 1000, 9)
                    cbar.set_ticks(tick_positions)
                    cbar.set_ticklabels([f"{t:.0f}" for t in tick_positions])

                    plt.axis('off')

                    # 在图像上添加两个矩形框
                    rect1 = plt.Rectangle((x1, y1), box_size, box_size, edgecolor=first_color,
                                          facecolor='none', linewidth=2)
                    rect2 = plt.Rectangle((x2, y2), box_size, box_size, edgecolor=second_color,
                                          facecolor='none', linewidth=2)
                    ax.add_patch(rect1)
                    ax.add_patch(rect2)

                    # 生成保存文件名（增加索引后缀）
                    output_filepath_with_index = output_filepath.replace(".png", f"_{i + 1}.png")
                    result_file.write(f"{os.path.basename(output_filepath_with_index)}: {steeper_text}\n")
                    plt.savefig(output_filepath_with_index, dpi=150, bbox_inches='tight', pad_inches=0)
                    plt.close()
                    print(f"图像已保存并缩放: {output_filepath_with_index}")
                    break


# 主函数
def main():
    csv_dir = r"F:\submit data\test pic\exp1\data"  # 存储 CSV 的目录
    target_ratios = [0.8, 0.83, 0.86, 0.9]  # 梯度比率
    blueyellow_name = "blueyellow"
    blueyellow = create_blueyellow_colormap()
    colormap_list = [
        'gray', 'Blues', 'hot', 'cubehelix', 'magma',
        'coolwarm', 'rainbow', 'spectral', blueyellow_name
    ]
    for colormap in colormap_list:
        # 动态处理自定义 colormap
        cmap_name = colormap
        folder = 'exp2'
        #folder = r'images\texp2'
        output_dir = r"..\..\color\{0}\{1}".format(folder, cmap_name)  # 输出图像文件夹
        result_filepath = os.path.join(output_dir, "result.txt")  # 结果文件路径
        os.makedirs(output_dir, exist_ok=True)
        with open(result_filepath, "w") as result_file:
            result_file.write("")  # 清空结果文件
        for csv_filename in os.listdir(csv_dir):
            if csv_filename.endswith(".csv"):
                csv_filepath = os.path.join(csv_dir, csv_filename)
                print(f"正在读取 CSV 文件: {csv_filepath}")
                # 不再重新归一化，使用 CSV 中的数据（生成时噪声在 [0,1000]）
                noise = np.loadtxt(csv_filepath, delimiter=",", skiprows=1)
                data_min, data_max = noise.min(), noise.max()
                noise = (noise - data_min) / (data_max - data_min)  # 先归一化到 [0,1]
                noise *= 1000  # 再放大到 [0,1000]
                output_filepath = os.path.join(output_dir,
                                               f"ScalarField_WithBoxes_{os.path.splitext(csv_filename)[0]}_{cmap_name}.png")
                # 动态选择 colormap
                if colormap == 'Blues':
                    colormap_used = 'Blues_r'
                elif colormap == 'blueyellow':
                    colormap_used = blueyellow
                elif colormap == 'rainbow':
                    colormap_used = 'rainbow'
                elif colormap == 'spectral':
                    colormap_used = 'nipy_spectral'
                else:
                    colormap_used = colormap
                generate_image_with_boxes_and_compare(noise, colormap_used, output_filepath, result_filepath,
                                                      target_ratios)
                # 此处不再调用 resize_to_448，因为各图在函数内已处理


if __name__ == "__main__":
    main()
