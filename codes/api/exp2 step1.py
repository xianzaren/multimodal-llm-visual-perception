import os
import cv2
import numpy as np
import re
from utils import extract_color_from_filename, combine_image_color1
from utils import client, get_png_paths, get_image_dict, write_answer_to_files2
from flask import send_file
import time
from openai import BadRequestError, OpenAIError


def retry_on_error(func, max_retries=3, initial_delay=5, backoff_factor=2):
    def wrapper(*args, **kwargs):
        retries = 0
        delay = initial_delay
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except (BadRequestError, OpenAIError) as e:
                retries += 1
                if retries >= max_retries:
                    raise e
                print(f"遇到错误: {e}. 重试 {retries}/{max_retries}... 等待 {delay} 秒")
                time.sleep(delay)
                delay = min(delay * backoff_factor, 60)  # 最大延迟60秒
    return wrapper

# 使用重试机制的请求函数
@retry_on_error
def send_request_with_retry(messages, max_retries=5, delay=10):
    return client.chat.completions.create(model="gpt-4o", messages=messages)

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
    # 修改正则表达式，支持解析两个坐标对
    rgb_match = re.findall(r'\((-?\d+(\.\d+)?), (-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\)', coord_str)
    # 如果没有找到有效的 RGB 值，设置默认值 (0.5, 0.5, 0.5) 和 (0.5, 0.5, 0.5)
    if len(rgb_match) == 0:
        print("未找到坐标，使用默认值 (0.5, 0.5, 0.5) 和 (0.5, 0.5, 0.5)")
        return [(0.5, 0.5, 0.5), (0.5, 0.5, 0.5)]  # 返回两个默认坐标
    # 如果只找到一个坐标，返回这个坐标和一个默认值 (0.5, 0.5, 0.5)
    elif len(rgb_match) == 1:
        R = float(rgb_match[0][0])
        G = float(rgb_match[0][2])
        B = float(rgb_match[0][4])
        print(f"只找到一个坐标: ({R}, {G}, {B}), 返回该坐标和默认值 (0.5, 0.5, 0.5)")
        return [(R, G, B), (0.5, 0.5, 0.5)]  # 返回一个找到的坐标和默认坐标
    # 如果找到两个坐标，则返回这两个坐标
    coordinates = []
    for match in rgb_match[:2]:  # 只取前两个坐标
        R = float(match[0])
        G = float(match[2])
        B = float(match[4])
        coordinates.append((R, G, B))

    return coordinates

# 处理数据
folder = 'exp2'
folder_path_exp1 = f"../../result/{folder}"
required_subfolders = [str(i) for i in range(1, 11)]
all_subfolders = [subfolder for subfolder in os.listdir(folder_path_exp1) if
                  os.path.isdir(os.path.join(folder_path_exp1, subfolder)) and subfolder in required_subfolders]
shape = (980, 630)
range = '[0,1000]'
values = ['1000', '0']  # 每次只找一个值
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
            all_found_points = []
            batch_size = 1
            prompt = (f"You are an image analysis assistant, and your task is to complete the following steps: "
                      f"1.I will provide a two-dimensional scalar field image, with dimensions of 987 pixels in width (horizontal) and 630 pixels in height (vertical). "
                      f"The image right side contains the colorbar legend. "
                      f"2. The numbered colorbar legend on the right represents the color mapping of {name}. The legend ranges from {legend} to [0 - 1000]. "
                      f"The color representing 0 is {bottom_color}, and the color representing 1000 is {top_color}; "
                      f"3. Core task:Your job is to analyse the color rgb of {values} in the colorbar by analyzing the colorbar legend."
                      f"Therefore, you need to read the colorbar legend on the right, especially the color corresponding to the value {values}."
                      f"4. The final output must strictly follow this format: (r1, g1, b1),(r2, g2, b2), representing the color value {values} in the colorbar legend."
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
                    print(f"解析坐标{coordinate}")
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
            write_answer_to_files2(result_file_path, input_image_path, all_found_points, is_first=False)
            print(all_found_points)
