import os

from codes.api.utils import extract_color_from_filename, combine_image_color1
from utils import client, get_png_paths, get_image_dict, write_answer_to_file

color_map_configs = {
    'gray': {
        "name": "gray",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    'hot': {
        "name": "hot",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    "rainbow": {
        "name": "rainbow",
        "bottom_color": "purple",
        "top_color": "red",
        "legend": "紫色到红色"
    },
    "Blues": {
        "name": "Blues_r",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "legend": "深蓝到浅蓝"
    },
    "coolwarm": {
            "name": "coolwarm",
            "bottom_color": "blue",
            "top_color": "red",
            "legend": "红色到蓝色"
        },
    "blueyellow": {
            "name": "从blue到yellow的自定义颜色映射表",
            "bottom_color": "blue",
            "top_color": "yellow",
            "legend": "蓝色到黄色"
        },
    "cubehelix": {
            "name": "cubehelix",
            "bottom_color": "very dark blue",
            "top_color": "white",
            "legend": "深蓝到白色"
        },
    "magma": {
            "name": "magma",
            "bottom_color": "very dark purple",
            "top_color": "light yellow",
            "legend": "深紫到明黄"
        },
    "spectral": {
            "name": "nipy_spectral",
            "bottom_color": "black",
            "top_color": "white",
            "legend": "黑色到白色"
        },
}

folder_path_exp1 = "../../result/2exp1"
#required_subfolders = ['30']
all_subfolders = os.listdir(folder_path_exp1)
#all_subfolders = [subfolder for subfolder in os.listdir(folder_path_exp1) if os.path.isdir(os.path.join(folder_path_exp1, subfolder)) and subfolder in required_subfolders]
batch_size = 5

for subfolder in all_subfolders:
    subfolder_path = os.path.join(folder_path_exp1, subfolder)
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
            bottom_color = colormap['bottom_color']
            top_color = colormap['top_color']
            legend = colormap['legend']
            # 设置message头
            messages = [
                {"role": "system", "content": f"You are ChatGPT, a large language model trained by OpenAI. "
                                              f"同时，你也是一个图像分析助手，你会为我完成以下工作："
                                              f"1. 我会每次为你提供{batch_size}张二维标量场的图片"
                                              f"包含图例，图例的变化范围从{legend}是[0 - 1]（已归一化），图例的名称是{name}，"
                                              f"其中，代表0的颜色为{bottom_color}，代表1的颜色为{top_color}；"
                                              f"标量场图像在坐标轴上的大小为820*630，若视为一个csv表格，则为630行，820列"
                                              f"（请注意820*630是标量场图像的坐标轴，而不是这张图片的坐标轴）"
                                              f"2. 你需要分析出相应的图例，从而方便判断各个颜色的数值"
                                              f"你需要在图左侧的标量场图上找出对应值为1.0, 0.8, 0.6, 0.4, 0.2的五个坐标，不要在colormap上寻找"
                                              f"找到的点尽量满足下面的条件"
                                              f"3. 边缘点限制： 标记点应距离图像边缘至少 20 个像素，以确保点位于图像的内部区域。"
                                              f"4. 区域多样性： 每个目标值的标记点应分布在图像的不同区域（如象限划分：左上、右上、左下、右下）"
                                              f"或尽量远离其他目标值的点，避免标记点过于集中。"
                                              f"5. 误差控制： 标记点对应的目标值在归一化后的图像中应尽量满足绝对误差 |目标值 - 像素值| < 0.05"
                                              f"若找不到则可以逐渐增大误差到0.6,0.7，以此类推..."
                                              f"6. 点距离限制： 每个目标值的标记点与其他目标值的标记点之间的欧几里得距离应不小于 50 像素，以确保点的空间分布更加分散。"
                                              f"7. 随机优选点： 如果某个目标值在多个像素点上均符合条件，则从中随机选择一个点，避免算法总是选择相同的点。"
                                              f"8. 你可以在图上查找相应颜色的位置，并给我相应的坐标，"
                                              f"输出格式为每张图片中五个值对应的五个坐标的列表，"
                                              f"其中每个坐标用 (x, y) 表示，x 横坐标，y代表纵坐标，x不应该大于820，y不应该大于630。"
                                              f"输出列表的格式为：[[x1, y1], [x2, y2], [x3, y3], [x4, y4], [x5, y5]]。"
                                              f"请确保输出严格遵循此格式，且列表中仅包含五个坐标，不要添加任何多余的文字和符号！"

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
            newanswer = answer.strip().replace("\n", "").replace(" ", "")
            append_content = combine_image_color1(image_list, newanswer)
            print(f"写入文件: {result_file_path}")
            write_answer_to_file(result_file_path, append_content, is_first=(index == 0))
            # index更新
            index += batch_size
