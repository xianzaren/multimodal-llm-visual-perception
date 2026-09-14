import os

from utils import extract_color_from_filename, combine_image_color2
from utils import client, get_png_paths, get_image_dict, write_answer_to_file
import ast

color_map_configs = {
    'gray': {
        "name": "gray",
        "color_box_1": "blue",
        "color_box_2": "red",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "black to white",
        "Ranges": [(1.000000, 1.000000, 1.000000), (0.752941, 0.752941, 0.752941), (0.501961, 0.501961, 0.501961), (0.250980, 0.250980, 0.250980), (0.000000, 0.000000, 0.000000)]
    },
    'hot': {
        "name": "hot",
        "color_box_1": "green",
        "color_box_2": "purple",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "black to white",
        "Ranges": [(1.000000, 1.000000, 1.000000), (1.000000, 1.000000, 0.027205), (1.000000, 0.359314, 0.000000), (0.700470, 0.000000, 0.000000), (0.041600, 0.000000, 0.000000)]
    },
    "rainbow": {
        "name": "rainbow",
        "color_box_1": "black",
        "color_box_2": "white",
        "bottom_color": "purple",
        "top_color": "red",
        "legend": "purple to red",
        "Ranges": [(1.000000, 0.000000, 0.000000),(1.000000, 0.700543, 0.378411),(0.503922, 0.999981, 0.704926),(0.001961, 0.709281, 0.923289),(0.500000, 0.000000, 1.000000)]
    },
    "Blues": {
        "name": "Blues_r",
        "color_box_1": "yellow",
        "color_box_2": "green",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "legend": "dark blue to pale blue",
        "Ranges": [(0.968627, 0.984314, 1.000000),(0.778685, 0.860300, 0.937993),(0.422745, 0.684075, 0.839892),(0.130427, 0.444152, 0.710327),(0.031373, 0.188235, 0.419608)]
    },
    "coolwarm": {
        "name": "coolwarm",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "red",
        "legend": "red to blue",
        "Ranges": [(0.705673, 0.015556, 0.150233),(0.956653, 0.598034, 0.477302),(0.867428, 0.864377, 0.862602),(0.554312, 0.690097, 0.995516),(0.229806, 0.298718, 0.753683)]
    },
    "blueyellow": {
        "name": "Custom color map from blue to yellow",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "yellow",
        "legend": "blue to yellow",
        "Ranges": [(0.988235, 0.988235, 0.000000), (0.756678, 0.744083, 0.244152), (0.521446, 0.496055, 0.492180), (0.286213, 0.248028, 0.740208), (0.050980, 0.000000, 0.988235)]
    },
    "cubehelix": {
        "name": "cubehelix",
        "color_box_1": "red",
        "color_box_2": "blue",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "legend": "very dark blue to white",
        "Ranges": [(1.000000, 1.000000, 1.000000), (0.777957, 0.706942, 0.931441), (0.632842, 0.474798, 0.290702), (0.085235, 0.326618, 0.297320), (0.000000, 0.000000, 0.000000)]
    },
    "magma": {
        "name": "magma",
        "color_box_1": "green",
        "color_box_2": "blue",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "legend": "very dark purple to light yellow",
        "Ranges": [(0.987053, 0.991438, 0.749504), (0.986700, 0.535582, 0.382210), (0.716387, 0.214982, 0.475290), (0.316654, 0.071690, 0.485380), (0.001462, 0.000466, 0.013866)]
    },
    "spectral": {
        "name": "nipy_spectral",
        "color_box_1": "white",
        "color_box_2": "black",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "balck to white",
        "Ranges": [(0.800000, 0.800000, 0.800000), (1.000000, 0.788235, 0.000000), (0.000000, 0.738531, 0.000000), (0.000000, 0.469314, 0.866700), (0.000000, 0.000000, 0.000000)]
    },
}

folder = 'exp2'
folder_path_exp2 = f"../../result/{folder}"
#all_subfolders = os.listdir(folder_path_exp2)
required_subfolders = ['1','2','10']
all_subfolders = [subfolder for subfolder in os.listdir(folder_path_exp2) if os.path.isdir(os.path.join(folder_path_exp2, subfolder)) and subfolder not in required_subfolders]
batch_size = 1

for subfolder in all_subfolders:
    subfolder_path = os.path.join(folder_path_exp2, subfolder)
    if os.path.isdir(subfolder_path):
        index = 0
        png_paths = get_png_paths(subfolder_path)
        while index < len(png_paths):
            # 获取colormap_name
            colormap_name = extract_color_from_filename(png_paths[index])
            # 设置写入的result文件
            result_file_path = f"{subfolder_path}/{colormap_name}.txt"
            reason_file_path = f"{subfolder_path}/{colormap_name}_reason.txt"  # 新的文件路径

            # 获取相应参数
            colormap = color_map_configs[colormap_name]
            range = colormap['Ranges']
            name = colormap['name']
            color_box_1 = colormap['color_box_1']
            color_box_2 = colormap['color_box_2']
            bottom_color = colormap['bottom_color']
            top_color = colormap['top_color']
            legend = colormap['legend']
            # 设置message头
            cotprompt = (f"You are an image analysis assistant, and your task is to complete the following steps: "
                         f"1. I will provide a two-dimensional scalar field image, with dimensions of 731 pixels in width (horizontal) and 449 pixels in height (vertical). "
                         f"The image is divided into two parts: the left side shows the scalar field visualization, and the right side contains the colorbar legend. "
                         f"2. The scalar field visualization contains two hollow square boxes, which color is {color_box_1} or {color_box_2} respectively. "
                         f"3. The coordinate system origin (0,0) is located at the lower-left corner, with the x-axis icreasing to the right and the y-axis growing upward. "
                         f"4. Core task:Your task is to analyze the color legend and determine which of the two boxes has a steeper color gradient."
                         f"This means identifying which box has a faster rate of change in the scalar color value."
                         f" You should focus on how quickly the color changes within each box, specifically the rate of change from the highest value to the lowest value"
                         f"the highest color is {top_color}, whose RGB is {range[0]}, the lowest color is {bottom_color}, whose RGB is {range[4]}."
                         f"5. The final output must strictly follow this format: ['{color_box_1}'] or ['{color_box_2}'], indicating the box with the steeper color gradient.")
            messages = [
                {"role": "system", "content": cotprompt
                 }
            ]
            images = get_image_dict(png_paths, index, batch_size)

            messages.append({"role": "user", "content": images})

            # 给gpt说明要求
            user_input = "根据我的要求给我相应的结果 格式不变 不要markdown格式加粗"
            messages.append(
                {"role": "user", "content": user_input}
            )
            print(cotprompt)
            # 返回结果
            completion = client.chat.completions.create(model="gpt-4o", messages=messages)
            answer = completion.choices[0].message.content
            print('System:', answer)

            # 提取颜色部分
            color_list_start = answer.find("[")
            color_list_end = answer.find("]") + 1  # 包含闭合括号
            color_string = answer[color_list_start:color_list_end]  # 提取颜色列表

            if color_string.startswith("[[") and color_string.endswith("]]"):
                color_string = color_string[1:-1]  # 去除最外层的中括号

            # 直接使用颜色列表，而不再使用 eval
            color_list = ast.literal_eval(color_string)  # color_string 已经是有效的列表格式，不需要再调用 eval()

            # 提取reason部分
            reason_start = answer.find("reason:")
            reason_content = answer[reason_start:] if reason_start != -1 else "No reason provided"

            # 将结果写入文件
            image_list =  png_paths[index:index+batch_size]
            append_content = combine_image_color2(image_list, color_list)
            print(f"写入文件: {result_file_path}")
            write_answer_to_file(result_file_path, append_content, is_first=(index == 0))

            # 将reason内容写入新文件
            print(f"写入文件: {reason_file_path}")
            write_answer_to_file(reason_file_path, reason_content, is_first=(index == 0))

            # 更新index
            index += batch_size