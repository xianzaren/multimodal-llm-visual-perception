import os

from utils import extract_color_from_filename, combine_image_color
from utils import client, get_png_paths, get_image_dict, write_answer_to_file

# 在处理answer时，先替换全角符号
def replace_fullwidth_characters(text):
    # 将全角字符转换为半角字符
    fullwidth_to_halfwidth = str.maketrans(
        "，。＂＃％＆＇（）＊＋，－．／０１２３４５６７８９：；＜＝＞？＠ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ［＼］＾＿｀ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ｛｜｝～",
        "，.＂＃％＆＇（）＊＋，－．／0123456789:；＜＝＞？＠ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}～"
    )
    return text.translate(fullwidth_to_halfwidth)

'''color_map_configs = {
    'greyscale': {
        "name": "greyscale",
        "color_box_1": "red",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    'bodyheat': {
        "name": "bodyheat",
        "color_box_1": "green",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    "rainbow": {
        "name": "rainbow",
        "bottom_color": "black",
        "top_color": "white",
        "color_box_1": "black",
        "legend": "紫色到红色"
    },
    "singlehue": {
        "name": "Blues_r",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "color_box_1": "red",
        "legend": "深蓝到浅蓝"
    },
    "coolwarm": {
        "name": "coolwarm",
        "bottom_color": "blue",
        "top_color": "red",
        "color_box_1": "green",
        "legend": "红色到蓝色"
    },
    "blueyellow": {
        "name": "从blue到yellow的自定义颜色映射表",
        "bottom_color": "blue",
        "top_color": "yellow",
        "color_box_1": "green",
        "legend": "蓝色到黄色"
    },
    "cubehelix": {
        "name": "cubehelix",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "color_box_1": "red",
        "legend": "深蓝到白色"
    },
    "extbodyheat": {
        "name": "extbodyheat",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "color_box_1": "green",
        "legend": "深紫到明黄"
    },
    "spectral": {
        "name": "nipy_spectral",
        "bottom_color": "black",
        "top_color": "white",
        "color_box_1": "black",
        "legend": "黑色到白色"
    },
}'''

color_map_configs = {
    'gray': {
        "name": "gray",
        "color_box_1": "red",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    'hot': {
        "name": "hot",
        "color_box_1": "green",
        "bottom_color": "black",
        "top_color": "white",
        "legend": "黑色到白色"
    },
    "rainbow": {
        "name": "rainbow",
        "bottom_color": "black",
        "top_color": "white",
        "color_box_1": "black",
        "legend": "紫色到红色"
    },
    "Blues": {
        "name": "Blues_r",
        "bottom_color": "dark blue",
        "top_color": "pale blue",
        "color_box_1": "red",
        "legend": "深蓝到浅蓝"
    },
    "coolwarm": {
        "name": "coolwarm",
        "bottom_color": "blue",
        "top_color": "red",
        "color_box_1": "green",
        "legend": "红色到蓝色"
    },
    "blueyellow": {
        "name": "从blue到yellow的自定义颜色映射表",
        "bottom_color": "blue",
        "top_color": "yellow",
        "color_box_1": "green",
        "legend": "蓝色到黄色"
    },
    "cubehelix": {
        "name": "cubehelix",
        "bottom_color": "very dark blue",
        "top_color": "white",
        "color_box_1": "red",
        "legend": "深蓝到白色"
    },
    "magma": {
        "name": "magma",
        "bottom_color": "very dark purple",
        "top_color": "light yellow",
        "color_box_1": "green",
        "legend": "深紫到明黄"
    },
    "spectral": {
        "name": "nipy_spectral",
        "bottom_color": "black",
        "top_color": "white",
        "color_box_1": "black",
        "legend": "黑色到白色"
    },
}

folder = 'nexp3'
folder_path_exp3 = f"../../result/{folder}"
all_subfolders = os.listdir(folder_path_exp3)
#all_subfolders = [subfolder for subfolder in os.listdir(folder_path_exp3) if
                  #os.path.isdir(os.path.join(folder_path_exp3, subfolder)) and subfolder in ['1', '10', '2']]
'''all_subfolders = [
    subfolder for subfolder in os.listdir(folder_path_exp3)
    if os.path.isdir(os.path.join(folder_path_exp3, subfolder)) and
    subfolder.isdigit() and (2 <= int(subfolder) <= 9 or 16 <= int(subfolder) <= 30)
]'''
batch_size = 1

for subfolder in all_subfolders:
    subfolder_path = os.path.join(folder_path_exp3, subfolder)
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
            color1 = colormap['color_box_1']
            bottom_color = colormap['bottom_color']
            top_color = colormap['top_color']
            legend = colormap['legend']
            baselineprompt = ("Imagine a line from A to B. Select the elevation profile below that most closely matches its slope."
                              "Finally, please provide the final result in the following format: ['Curve x is the correct curve'...] containing a list with one result.")
            cotprompt = (f"You are ChatGPT, a large language model trained by OpenAI."
                      f"At the same time, you are also an image analysis assistant, and you will perform the following tasks for me:"
                      f"1. I will provide you with {batch_size} images of 2D scalar fields with six curves each time."
                      f"Each image is divided into a scalar field visualization on the left, a colorbar legend on the right of the scalar field visualization, and six curves."
                      f"The scalar field visualization on the left does not include the white padding along the edges of the image."
                      f"The colorbar with numbers on the right is the legend, and the legend is not considered part of the scalar field visualization."
                      f"2. The colorbar legend on the right with numbers represents the color mapping of {name}, with the legend range from {legend} being [0 - 1] (normalized), and the name of the legend is {name},"
                      f"where the color representing 0 is {bottom_color} and the color representing 1 is {top_color}."
                      f"You need to analyze the corresponding legend to map the values to the colors."
                      f"In the scalar field image, the colors represent values, and the correspondence between colors and values is the same as in the legend."
                      f"3. I have marked two {color1} points on the image, labeled point A and point B."
                      f"Assume there is a straight line between points A and B. Based on the colors in the image, predict the values of each pixel along the line from A to B; these values will form a curve on the coordinate axis."
                      f"4. The six curves on the right represent the data variation along the straight line between points A and B, and only one of these curves is the correct one."
                      f"You can first determine the values at points A and B, locate their positions on the coordinate axis and their relative positions, and then gradually infer the trend of the curve."
                      f"By using the colors and color changes between points A and B, determine the positions on the y-axis corresponding to the values of these points and the trend of the straight line between them."
                      f"You can estimate the position and trend of a segment of the curve by identifying special points such as extrema and inflection points."
                      f"The segments of the curve obtained through such piecewise analysis should be able to be combined into a complete curve."
                      f"By analyzing the trend and position of the curves, you should be able to select the correct curve."
                      f"5. Finally, please provide the result in the following format: ['Curve x is the correct curve'...] — a list containing one result.")
            # 设置message头
            messages = [
                {"role": "system", "content": baselineprompt
                 }
            ]

            # 编码后的 batch 张图片
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

            # 打印结果
            print('System:', answer)

            # 提取reason部分
            reason_start = answer.find("reason:")
            reason_content = answer[reason_start:] if reason_start != -1 else "No reason provided"
            # 提取出曲线的部分
            answer_content = answer[:reason_start].strip() if reason_start != -1 else answer.strip()

            # 然后将answer_content和reason_content分别处理
            image_list = png_paths[index:index + batch_size]
            answer_content = replace_fullwidth_characters(answer_content)
            append_content = combine_image_color(image_list, answer_content)  # 仅包含曲线的内容

            # 将结果写入文件
            reason_content = replace_fullwidth_characters(reason_content)
            print(f"写入文件: {result_file_path}")
            write_answer_to_file(result_file_path, append_content, is_first=(index == 0))

            # 将reason内容写入新文件
            print(f"写入文件: {reason_file_path}")
            write_answer_to_file(reason_file_path, reason_content, is_first=(index == 0))
            # 更新index
            index += batch_size



'''"You are ChatGPT, a large language model trained by OpenAI."
                                              "同时，你也是一个图像分析助手，你会为我完成以下工作"
                                              f"1.我会每次为你提供{batch_size}张带有六条曲线的二维标量场的图片"
                                              f"这张图分为位于左侧的标量场可视化图像,位于标量场可视化图像右侧颜色图例和六条曲线"
                                              f"左侧标量场可视化图像不包括图像边缘的白色填充"
                                              f"右侧标有数字的colorbar为图例，图例不视为标量场可视化图像的一部分。"
                                              f"2.右侧标有数字的colorbar图例代表{name}的颜色映射情况，图例的变化范围从{legend}是[0 - 1]（已归一化），图例的名称是{name}，"
                                              f"其中，代表0的颜色为{bottom_color}，代表1的颜色为{top_color}。"
                                              f"你需要分析出相应的图例，将数值和颜色对应起来。"
                                              f"标量场图像中的颜色代表数值，标量场图像中的颜色与数值的对应关系与图例相同"
                                              f"3.我在图上标出了两个{color1}的点，分别为A点与B点"
                                              f"假设AB两点间有一条直线，请基于图像中的颜色，预测a-b之间各像素点的数值，这些数值会在坐标轴上生成一条曲线"
                                              f"4.右侧的六条曲线代表了AB两点间直线的数据变化,其中只有一条曲线是正确的曲线。"
                                              f"你可以先定位AB两点的值，定位AB两点在坐标轴上的位置和相对位置，然后逐渐判断曲线的走向"
                                              f"通过AB两点之间的颜色和颜色变化定位这些点所对应的值在y坐标轴上的位置，和AB两点直线的趋势"
                                              f"你可以通过寻找极值，转折点等特殊点预估某段曲线的位置和走向"
                                              f"通过这样一段段距离的分析得到的一段段曲线应该可以合成一整条曲线"
                                              f"通过分析曲线趋势和位置，你应该可以选择出正确的曲线"
                                              f"5.最后结果请给我如下格式的结果: ['曲线x是正确的曲线'...] 含有1结果的列表"'''