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
        "legend": "黑色到白色"
    },
    'hot': {
        "name": "hot",
        "color_box_1": "green",
        "color_box_2": "purple",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    "rainbow": {
        "name": "rainbow",
        "color_box_1": "black",
        "color_box_2": "white",
        "bottom_color": "purple",
        "top_color": "red",
        "legend": "紫色到红色"
    },
    "Blues": {
        "name": "Blues_r",
        "color_box_1": "yellow",
        "color_box_2": "green",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "legend": "深蓝到浅蓝"
    },
    "coolwarm": {
        "name": "coolwarm",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "red",
        "legend": "红色到蓝色"
    },
    "blueyellow": {
        "name": "从blue到yellow的自定义颜色映射表",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "yellow",
        "legend": "蓝色到黄色"
    },
    "cubehelix": {
        "name": "cubehelix",
        "color_box_1": "red",
        "color_box_2": "blue",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "legend": "深蓝到白色"
    },
    "magma": {
        "name": "magma",
        "color_box_1": "green",
        "color_box_2": "blue",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "legend": "紫黑到明黄"
    },
    "spectral": {
        "name": "nipy_spectral",
        "color_box_1": "white",
        "color_box_2": "black",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "紫色到红色"
    },
}

folder = 'exp2'
folder_path_exp2 = f"../../result/{folder}"
#all_subfolders = os.listdir(folder_path_exp2)
required_subfolders = ['10', '2']
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
            name = colormap['name']
            color_box_1 = colormap['color_box_1']
            color_box_2 = colormap['color_box_2']
            bottom_color = colormap['bottom_color']
            top_color = colormap['top_color']
            legend = colormap['legend']
            # 设置message头
            baselineprompt = (f"Terrain is steeper when there is larger change in elevation between adjacent points. "
                             f"Compare the steepness of terrain inside the two boxes, then choose the box that is steeper on average."
                             f"Finally, just provide the result in the following format: [{color_box_1} or {color_box_2}]")
            cotprompt = (f"You are an image analysis assistant, and your task is to complete the following steps: "
                         f"1. I will provide a two-dimensional scalar field image, with dimensions of 731 pixels in width (horizontal) and 449 pixels in height (vertical). "
                         f"The image is divided into two parts: the left side shows the scalar field visualization, and the right side contains the colorbar legend. "
                         f"2. The scalar field visualization contains two hollow square boxes, which color is {color_box_1} or {color_box_2} respectively. "
                         f"3. The coordinate system origin (0,0) is located at the lower-left corner, with the x-axis icreasing to the right and the y-axis growing upward. "
                         f"4. Core task:Your task is to analyze the color legend and determine which of the two boxes has a steeper color gradient."
                         f"This means identifying which box has a faster rate of change in the scalar color value."
                         f" You should focus on how quickly the color changes within each box, specifically the rate of change from the highest value to the lowest value"
                         f"5. The final output must strictly follow this format: [{color_box_1}] or [{color_box_2}], indicating the box with the steeper color gradient. you must answer the question in English")
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

            # 返回结果
            completion = client.chat.completions.create(model="gpt-4o", messages=messages)
            answer = completion.choices[0].message.content
            print('System:', answer)

            color_list_start = answer.find("[")
            color_list_end = answer.find("]") + 1  # 包含闭合括号
            color_string = answer[color_list_start:color_list_end]  # 提取颜色列表

            # 确保颜色列表中的内容是字符串格式
            color_string = color_string.replace("yellow", '"yellow"').replace("green", '"green"') \
                .replace("purple", '"purple"').replace("blue", '"blue"') \
                .replace("red", '"red"').replace("black", '"black"') \
                .replace("white", '"white"')

            # 将颜色字符串转换为列表
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

'''f"你是一个图像分析助手，你会为我完成以下工作："
                                              f"1. 我会每次为你提供{batch_size}张二维标量场的图片,"
                                              f"这张图分为位于左侧的标量场可视化图像和位于右侧颜色图例，左侧标量场可视化图像不包括图像边缘的白色填充，"
                                              f"右侧标有数字的colorbar为图例，图例不视为标量场可视化图像的一部分。"
                                              f"2.右侧标有数字的colorbar图例代表{name}的颜色映射情况，图例的变化范围从{legend}是[0 - 1]（已归一化），图例的名称是{name}，"
                                              f"其中，代表0的颜色为{bottom_color}，代表1的颜色为{top_color}。"
                                              f"你需要分析出相应的图例，将数值和颜色对应起来。"
                                              f"标量场图像中的颜色代表数值，标量场图像中的颜色与数值的对应关系与图例相同"
                                              f"3.我在标量场图上分别用{color_box_1}和{color_box_2}正方形框框出来两个区域，你需要根据分析出的图例，"
                                              f"结合框内的颜色，判断出两个框内哪个框的陡峭程度更高，也就是哪个方框内的数值变化速率更大，"
                                              f"也就是哪个框内的颜色变化更快，或者说在一定范围内变化幅度更大"
                                              f"你可以通过颜色表和标量场中的颜色对应得到方框内某点的值"
                                              f"4.最后只需要给我如下格式的结果: ['{color_box_1} 或者 {color_box_2}'...]含有四个结果的列表，"
                                              f"颜色结果必须用引号包裹"
cotprompt = (f"You are an image analysis assistant, and you will do the following for me:"
                      f"1. I will provide you with {batch_size} 2D scalar field images each time. Each image has a horizontal length of 1112 pixels and a vertical width of 920 pixels"
                      f"The coordinate system is defined such that the origin (0,0) is located at the bottom-left corner of the image, with the x-axis increasing to the right and the y-axis increasing upward (image coordinate system)\n"
                      f"Image structure: On the left side is the main scalar field visualization of 820*630 pixels (effective area), and on the right side is the vertical colorbar legend.\n"
                      f"The scalar field visualization on the left does not include the white padding around the image, and the colorbar on the right with numbers is the legend, which is not considered part of the scalar field visualization."
                      f"2. The colorbar legend on the right with numbers represents the color mapping of {name}, with the legend range {legend} being [0 - 1] (normalized). The name of the legend is {name}, where the color representing 0 is {bottom_color}, and the color representing 1 is {top_color};"
                      f"3. I use square boxes on the image to enclose two regions, labeled Box A and Box B"
                      f"4. The core task: You need to analyze the legend, together with the colors inside the square boxes, to determine which box has a higher degree of steepness—i.e., which box has a greater rate of change in scalar values"
                      f"4. Finally, you only need to provide the result in the following format: [\"A\"] or [\"B\"]"
                      f"Note that you only need to choose one from A or B, namely the one whose box has a larger rate of change in scalar values."
                      f"Note that you must choose either A or B; you cannot choose neither, nor can you choose both.")'''
'''color_map_configs = {
    'greyscale': {
        "name": "greyscale",
        "color_box_1": "blue",
        "color_box_2": "red",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    'bodyheat': {
        "name": "bodyheat",
        "color_box_1": "green",
        "color_box_2": "purple",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    "rainbow": {
        "name": "rainbow",
        "color_box_1": "black",
        "color_box_2": "white",
        "bottom_color": "purple",
        "top_color": "red",
        "legend": "紫色到红色"
    },
    "singlehue": {
        "name": "Blues_r",
        "color_box_1": "yellow",
        "color_box_2": "green",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "legend": "深蓝到浅蓝"
    },
    "coolwarm": {
        "name": "coolwarm",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "red",
        "legend": "红色到蓝色"
    },
    "blueyellow": {
        "name": "从blue到yellow的自定义颜色映射表",
        "color_box_1": "purple",
        "color_box_2": "green",
        "bottom_color": "blue",
        "top_color": "yellow",
        "legend": "蓝色到黄色"
    },
    "cubehelix": {
        "name": "cubehelix",
        "color_box_1": "red",
        "color_box_2": "blue",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "legend": "深蓝到白色"
    },
    "extbodyheat": {
        "name": "magma",
        "color_box_1": "green",
        "color_box_2": "blue",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "legend": "深紫到明黄"
    },
    "spectral": {
        "name": "nipy_spectral",
        "color_box_1": "black",
        "color_box_2": "white",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
}'''