import os

from codes.api.utils import extract_color_from_filename, combine_image_color
from utils import client, get_png_paths, get_image_dict, write_answer_to_file

color_map_configs = {
    'gray' :{
        "name": "gray",
        "color_box_1" : "blue",
        "color_box_2" : "red",
        "bottom_color" : "black",
        "top_color" : "white",
        "legend" : "黑色到白色"
    },
    'hot' : {
        "name":"hot",
        "color_box_1" : "green",
        "color_box_2" : "purple",
        "bottom_color" : "black",
        "top_color" : "white",
        "legend" : "黑色到白色"
    },
    "rainbow" : {
        "name":"rainbow",
        "color_box_1" : "black",
        "color_box_2" : "white",
        "bottom_color" : "purple",
        "top_color" : "red",
        "legend" : "紫色到红色"
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
    "magma" : {
        "name":"magma",
        "color_box_1" : "green",
        "color_box_2" : "blue",
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

folder_path_exp2 = "../../result/exp2"
all_subfolders = os.listdir(folder_path_exp2)
batch_size = 4

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
            # 获取相应参数
            colormap = color_map_configs[colormap_name]
            name = colormap['name']
            color_box_1 = colormap['color_box_1']
            color_box_2 = colormap['color_box_2']
            bottom_color = colormap['bottom_color']
            top_color = colormap['top_color']
            legend = colormap['legend']

            # 设置message头
            messages = [
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."
                                              "同时，你也是一个图像分析助手，你会为我完成以下工作"
                                              f"1.我会每次为你提供{batch_size}张二维标量场的图片，包含图例"
                                              f"图例的变化范围从{legend}是[0 - 1],图例名称为{name}"
                                              f"其中，代表0的颜色为{bottom_color}，代表1的颜色为{top_color}"
                                              "2.你需要分析出相应的图例，从而方便判断各个颜色的数值"
                                              f"3.我在图上分别用{color_box_1}和{color_box_2}正方形框框出来两个区域，你需要根据分析出的图例，"
                                              f"结合框内的颜色，判断出两个框内哪个框的陡峭程度更高，也就是哪个方框内的标量值变化速率更大"
                                              f"你可以通过颜色表和标量场中的颜色对应得到方框内某点的值"
                                              f"4.最后只需要给我如下格式的结果: ['{color_box_1} / {color_box_2}'...]含有四个结果的列表,"
                                              f"颜色结果必须用引号包裹"
                 }
            ]

            # 编码后的 batch 张图片
            images = get_image_dict(png_paths, index, batch_size)

            messages.append({"role": "user",
                                "content": images,
                            })

            # 给gpt说明要求
            user_input = "根据我的要求给我相应的结果 格式不变 不要markdown格式加粗"
            messages.append(
                {"role": "user", "content": user_input}
            )
            # 返回结果
            completion = client.chat.completions.create(model="gpt-4o", messages=messages)
            answer = completion.choices[0].message.content
            # 打印结果
            print('System:', answer)
            # 将结果写入文件
            image_list =  png_paths[index:index+batch_size]
            append_content = combine_image_color(image_list, answer)
            print(f"写入文件: {result_file_path}")
            write_answer_to_file(result_file_path, append_content, is_first=(index == 0))
            # index更新
            index += batch_size