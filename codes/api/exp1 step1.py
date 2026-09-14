import os
import cv2
import numpy as np
import re
from utils import extract_color_from_filename, combine_image_color1
from utils import client, get_png_paths, get_image_dict, write_answer_to_file1
from flask import send_file
import time
from openai import BadRequestError

def retry_on_error(func, max_retries=3, delay=5):
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except BadRequestError as e:
                retries += 1
                if retries >= max_retries:
                    raise e
                print(f"遇到错误: {e}. 重试 {retries}/{max_retries}...")
                time.sleep(delay)
    return wrapper

# 使用重试机制的请求函数
@retry_on_error
def send_request_with_retry(messages):
    return client.chat.completions.create(model="gpt-4o", messages=messages)

# 颜色映射表
color_map_configs = {
    'gray': {"name": "gray", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
    'hot': {"name": "hot", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
    "rainbow": {"name": "rainbow(jet)", "bottom_color": "purple", "top_color": "red", "legend": "purple to red"},
    "Blues": {"name": "Blues_r", "bottom_color": "dark blue", "top_color": "pale blue", "legend": "dark blue to pale blue"},
    "coolwarm": {"name": "coolwarm", "bottom_color": "blue", "top_color": "red", "legend": "red to blue"},
    "blueyellow": {"name": "blueyellow", "bottom_color": "blue", "top_color": "yellow", "legend": "blue to yellow"},
    "cubehelix": {"name": "cubehelix", "bottom_color": "very dark blue", "top_color": "white", "legend": "very dark blue to white"},
    "magma": {"name": "extbodyheat(like magma)", "bottom_color": "very dark purple", "top_color": "light yellow", "legend": "very dark purple to light yellow"},
    "spectral": {"name": "spectral_r", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
}

# 替换全角字符
def replace_fullwidth_characters(text):
    fullwidth_to_halfwidth = str.maketrans("，。［］（）", ",.[]()")
    return text.translate(fullwidth_to_halfwidth)

def clean_and_parse_coordinates(coord_str):
    coord_str = coord_str.strip()
    # 匹配格式：只有数字的 RGB (例如 (0.75, 0.75, 0.75) 或 (100, 200, 255))
    rgb_match = re.search(r'\((-?\d+(\.\d+)?), (-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\)', coord_str)
    # 如果没有找到 RGB 格式，设置默认值 (0, 0, 0)
    if not rgb_match:
        print(f"未找到有效的 RGB 值，使用默认值 (0, 0, 0)")
        return (0, 0, 0)
    # 提取 RGB 值并转换为浮点数
    R = float(rgb_match.group(1))
    G = float(rgb_match.group(3))
    B = float(rgb_match.group(5))
    return (R, G, B)

# 处理数据
folder = 'fill'
folder_path_exp1 = f"../../result/{folder}"
required_subfolders = [str(i) for i in range(1, 11)]
#required_subfolders = [str(i) for i in range(7, 10)]
all_subfolders = [subfolder for subfolder in os.listdir(folder_path_exp1) if
                  os.path.isdir(os.path.join(folder_path_exp1, subfolder)) and subfolder in required_subfolders]
shape = (980, 630)
range = '[0,1000]'
values = ['1000', '750', '500', '250', '0']  # 每次只找一个值
for subfolder in all_subfolders:
    subfolder_path = os.path.join(folder_path_exp1, subfolder)
    if os.path.isdir(subfolder_path):
        png_paths = get_png_paths(subfolder_path)

        for input_image_path in png_paths:
            colormap_name = extract_color_from_filename(input_image_path)  # **获取 colormap 名称**
            config = color_map_configs.get(colormap_name)
            name = config['name']
            legend = config['legend']
            bottom_color = config['bottom_color']
            top_color = config['top_color']
            if colormap_name not in color_map_configs:
                print(f"❌ 未找到 {colormap_name} 的 colormap 配置，跳过此文件。")
                continue

            # **使用 colormap 作为 txt 文件名**
            if colormap_name == 'Blues':
                filename = 'singlehue'
            elif colormap_name == 'magma':
                filename = 'extbodyheat'
            elif colormap_name == 'hot':
                filename = 'bodyheat'
            elif colormap_name == 'gray':
                filename = 'greyscale'
            else:
                filename = colormap_name
            result_file_path = os.path.join(subfolder_path, f"{filename}.txt")

            filename_without_ext, ext = os.path.splitext(os.path.basename(input_image_path))
            marked_image_path = os.path.join(subfolder_path, f"marked_{filename_without_ext}{ext}")
            all_found_points = []  # 存储 5 次搜索的坐标
            batch_size = 1
            for value in values:  # 逐个值查找
                prompt = (f"You are an image analysis assistant, and your task is to complete the following steps: "
                          f"1.I will provide a two-dimensional scalar field image, with dimensions of 987 pixels in width (horizontal) and 630 pixels in height (vertical). "
                          f"The image right side contains the colorbar legend. "
                          f"2. The numbered colorbar legend on the right represents the color mapping of {name}. The legend ranges from {legend} to [0 - 1000]. "
                          f"The color representing 0 is {bottom_color}, and the color representing 1000 is {top_color}; "
                          f"3. Core task:Your job is to analyse the color rgb of {value} in the colorbar by analyzing the colorbar legend."
                          f"Therefore, you need to read the colorbar legend on the right, especially the color corresponding to the value {value}."
                          f"4. The final output must strictly follow this format: (r1, g1, b1), representing the color value {value} in the colorbar legend."
                          f"Each rgb should be represented as (r, g, b), where r,g and b are within the range: r∈(0, 1), g∈(0, 1), b∈(0, 1) "
                          f"Please ensure the output strictly follows this format without any extra text or symbols.")
                messages = [
                    {"role": "system", "content": prompt
                     }
                                                            ]
                images = get_image_dict([input_image_path], 0, 1)
                messages.append({"role": "user", "content": images})
                messages.append({"role": "user", "content": "请按照上述要求给出坐标。"})
                print(prompt)
                # 发送请求
                try:
                    completion = send_request_with_retry(messages)
                    answer = completion.choices[0].message.content.strip()
                    print(f'GPT 结果: {answer}')

                    # 解析坐标
                    try:
                        coordinate = clean_and_parse_coordinates(answer)
                        all_found_points.append(coordinate)
                    except Exception as e:
                        # 当解析失败时，使用默认值 [0,0]
                        coordinate = clean_and_parse_coordinates('[0,0]')
                        all_found_points.append(coordinate)
                        print("坐标解析失败:", e)
                        continue
                except BadRequestError as e:
                    print(f"请求失败: {e}")
                    continue

            # 画图
            '''draw_marked_image(input_image_path, all_found_points, marked_image_path)
            print(f"✅ 标记后的图像已保存: {marked_image_path}")'''

            # **✅ 追加写入 `color.txt`，确保多个图片数据不会被覆盖**
            formatted_result = f"{input_image_path}: {all_found_points}\n"
            write_answer_to_file1(result_file_path, input_image_path, all_found_points, is_first=False)
