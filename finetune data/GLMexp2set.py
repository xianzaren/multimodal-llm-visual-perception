import json
import os
import gc
import re
import base64

colormap_list = [
    'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]

color_map_configs = {
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
}

'''color_map_configs = {
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
        "color_box_1": "red",
        "color_box_2": "blue",
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
        "color_box_1": "red",
        "color_box_2": "blue",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "legend": "深紫到明黄"
    },
    "spectral": {
        "name": "nipy_spectral",
        "color_box_1": "blue",
        "color_box_2": "red",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
}

colormap_list = [
    'gray', 'Blues', 'hot', 'cubehelix', 'magma',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]'''


def parse_expected_results(file_path):
    results = {}
    if not os.path.exists(file_path):
        print(f"❌ 期望结果文件未找到: {file_path}")
        return results  # 返回空字典
    print(f"\n📂 读取期望结果文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r"^(.*\.png)\s*:\s*(.+?) Box Avg$", line)
            if match:
                imgname = match.group(1)
                filename = re.sub(r'\.png$', '', imgname)
                ans = match.group(2)
                color = ans.lower()
                results[filename] = color
    return results

prompt = 'cot'
kind = 'train'
source_folder = 'exp2'
target_floder = 'nexp2'
base_path = f'images/{source_folder}'
output_file = f"dataset/{prompt}/file-GLM-finetune_exp2_{kind}_{prompt}.jsonl"
id_counter = 0

if os.path.exists(output_file):
    os.remove(output_file)

# 定义用户 prompt（baselineprompt）
baselineprompt = "Compare the steepness of terrain inside the two boxes, then choose the box that is steeper on average. Give me the box color."

def process_file(cm):
    global id_counter
    cm_path = os.path.join(base_path, cm)
    png_files = [f for f in os.listdir(cm_path) if f.endswith('.png')]

    res_path = os.path.join(cm_path, "result.txt")
    ans = parse_expected_results(res_path)

    for png_file in png_files:
        image_filename = os.path.splitext(png_file)[0]  # 获取不带后缀的文件名

        # 使用解析得到的结果作为期望答案，若找不到则返回 'unknown'
        coord_str = ans.get(image_filename, 'unknown')  # 直接提取答案，如 Yellow 或 Green
        batch_size = 1
        colormap = color_map_configs[cm]
        name = colormap['name']
        color_box_1 = colormap['color_box_1']
        color_box_2 = colormap['color_box_2']
        cotprompt = (f"You are an image analysis assistant, and you will complete the following tasks for me: "
                     f"1. I will provide you with {batch_size} images of 2D scalar fields at a time, "
                     f"each image is divided into two parts: the scalar field visualization on the left and the color legend on the right. "
                     f"The scalar field visualization on the left does not include the white padding around the image edges, "
                     f"and the numbered colorbar on the right serves as the legend, which is not considered part of the scalar field visualization. "
                     f"2. The numbered colorbar legend on the right represents the color mapping for {name}. The legend's range is from  [0 - 1000], and the legend is named {name}, "
                     f"You need to analyze the legend to map the values to their corresponding colors. "
                     f"The colors in the scalar field image represent values, and the mapping between colors and values is the same as in the legend. "
                     f"3. I have marked two regions on the scalar field image with square boxes of {color_box_1} and {color_box_2}. Based on the analyzed legend, "
                     f"and by examining the colors within the boxes, determine which of the two boxes has a steeper gradient—that is, which box has a higher rate of change in values, "
                     f"or in other words, which box shows a faster color change or a larger range of variation over a given interval. "
                     f"You can determine the value at any point within the box using the correspondence between the colors in the color table and those in the scalar field image. "
                     f"4. Finally, just provide the result in the following format: ['{color_box_1} or {color_box_2}', ...]—a list containing a result, "
                     f"with the color results enclosed in single quotes, not without quotes. must like be ['yellow'], not [yellow]")

        # 构造新的 JSON 格式
        json_data = {
            "messages": [
                {"role": "user", "content": cotprompt,
                 "image": f"/{target_floder}/{cm}/{png_file}"},  # 直接使用图片文件名
                {"role": "assistant", "content": coord_str}  # 直接将颜色答案填入
            ]
        }

        with open(output_file, 'a', encoding='utf-8') as f_out:
            f_out.write(json.dumps(json_data, ensure_ascii=False) + "\n")
        print(f"记录了 {id_counter} 条数据")
        id_counter += 1

for cm in colormap_list:
    process_file(cm)

print(f"数据集已成功保存为 {output_file}")
