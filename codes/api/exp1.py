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

color_map_configs = {
    'gray': {"name": "gray", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
    'hot': {"name": "hot", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
    "rainbow": {"name": "rainbow", "bottom_color": "purple", "top_color": "red", "legend": "purple to red"},
    "Blues": {"name": "Blues_r", "bottom_color": "dark blue", "top_color": "pale blue", "legend": "dark blue to pale blue"},
    "coolwarm": {"name": "coolwarm", "bottom_color": "blue", "top_color": "red", "legend": "red to blue"},
    "blueyellow": {"name": "blueyellow", "bottom_color": "blue", "top_color": "yellow", "legend": "blue to yellow"},
    "cubehelix": {"name": "cubehelix", "bottom_color": "very dark blue", "top_color": "white", "legend": "very dark blue to white"},
    "magma": {"name": "magma", "bottom_color": "very dark purple", "top_color": "light yellow", "legend": "very dark purple to light yellow"},
    "spectral": {"name": "nipy_spectral", "bottom_color": "black", "top_color": "white", "legend": "black to white"},
}

# 替换全角字符
def replace_fullwidth_characters(text):
    fullwidth_to_halfwidth = str.maketrans("，。［］（）", ",.[]()")
    return text.translate(fullwidth_to_halfwidth)


# 解析 GPT 返回的坐标
def clean_and_parse_coordinates(coord_str):
    """
    从输入字符串中提取第一个匹配到的方括号内的数字作为坐标。
    支持的格式包括：
      - "[38, 7]"
      - "[x, y] = [38, 7]"
      - "[x=738, y=675]"

    例如，若输入字符串为：
      "GPT 结果: 图中标示为“250”的颜色对应的点位于大致图像中下方偏左位置。该点的坐标估算为[x, y]：
       [360, 500]"
    则会首先找到 "[360, 500]"，并解析出坐标 (360, 500)。
    """
    # 移除前后空白
    coord_str = coord_str.strip()
    # 使用正则表达式查找第一个完整的方括号内容
    bracket_match = re.search(r'\[[^\]]*\]', coord_str)
    if not bracket_match:
        raise ValueError("无法找到方括号内的内容")
    bracket_content = bracket_match.group()  # 例如 "[360, 500]"
    # 从方括号内容中提取所有整数（包括负数）
    numbers = re.findall(r'-?\d+', bracket_content)
    if len(numbers) < 2:
        raise ValueError(f"无法解析坐标: {bracket_content}")
    x, y = int(numbers[0]), int(numbers[1])
    return (x, y)

# 画图
def draw_marked_image(original_image_path, points, output_path):
    image = cv2.imread(original_image_path)
    if image is None:
        print(f"无法加载图像: {original_image_path}")
        return None

    colors = [(255, 0, 0), (0, 255, 255), (0, 0, 255), (0, 255, 0), (128, 0, 128)]
    radius = 5
    thickness = -1

    for i, (x, y) in enumerate(points):
        color = colors[i % len(colors)]
        cv2.circle(image, (x, y), radius, color, thickness)
        cv2.putText(image, f'({x},{y})', (x + 10, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    cv2.imwrite(output_path, image)
    return output_path

# 处理数据
folder = 'exp1'
folder_path_exp1 = f"../../result/{folder}"
required_subfolders = [str(i) for i in range(8, 10)]
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
            result_file_path = os.path.join(subfolder_path, f"{colormap_name}.txt")

            filename_without_ext, ext = os.path.splitext(os.path.basename(input_image_path))
            marked_image_path = os.path.join(subfolder_path, f"marked_{filename_without_ext}{ext}")
            all_found_points = []  # 存储 5 次搜索的坐标
            batch_size = 1
            baselineprompt = (f"Find the a coordinate of the point with the value {value} in the scalar field image."
                             f"The final output must strictly follow this format: [x, y], representing the coordinates of the color value {value} in the scalar field image. "
                             f"Each coordinate should be represented as (x, y), where x and y are positive integers within the range: x∈(0, 820), y∈(0, 630). "
                             f"Please ensure the output strictly follows this format (x, y).")
            cotprompt = (f"1. I will provide a two-dimensional scalar field image, with dimensions of {shape[0]} pixels in width (horizontal) and {shape[1]} pixels in height (vertical). "
                        f"The image is divided into two parts: the left side shows the scalar field visualization, and the right side contains the colorbar legend. "
                        f"2. The scalar field on the left side has dimensions of 820 pixels in width and 630 pixels in height. "
                        f"The scalar field visualization does not include the white fill area on the right, which is reserved for the legend, "
                        f"so the legend should not be considered as a part of the scalar field. "
                        f"3. The numbered colorbar legend on the right represents the color mapping of {name}. The legend ranges from {legend} to {range}. "
                        f"The color representing 0 is {bottom_color}, and the color representing 1 is {top_color}; "
                        f"4. The coordinate system origin (0,0) is located at the upper-left corner, with the x-axis growing to the right and the y-axis growing downward. "
                        f"5. Core task: Your job is to find the coordinates of a point with the value {value} in the scalar field image by analyzing the color legend. "
                        f"Therefore, you need to read the legend on the right, especially the color corresponding to the value {value}. "
                        f"6. The final output must strictly follow this format: [x1, y1], representing the coordinates of the color value {value} in the scalar field image. "
                        f"Each coordinate should be represented as (x, y), where x and y are positive integers within the range: x∈(0, 820), y∈(0, 630). "
                        f"Please ensure the output strictly follows this format without any extra text or symbols. The coordinate values must be returned and should not exceed the specified range."
)
            for i, value in values:  # 逐个值查找
                messages = [
                    {"role": "system", "content": baselineprompt
                     }
                                                            ]
                images = get_image_dict([input_image_path], 0, 1)
                messages.append({"role": "user", "content": images})
                messages.append({"role": "user", "content": "请按照上述要求给出坐标。"})

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
