import base64
import os
import re
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# 从 txt 文件读取 API 信息
def read_api_info_from_txt(file_path="api_info.txt"):
    with open(file_path, "r") as file:
        lines = file.readlines()
        base_url = None
        api_key = None
        for line in lines:
            if line.startswith("base_url="):
                base_url = line.strip().split("=")[1]
            elif line.startswith("api_key="):
                api_key = line.strip().split("=")[1]
        return base_url, api_key

def get_png_paths(folder_path):
    # 使用 os.listdir 获取文件夹下的所有文件和文件夹的名称
    all_files = os.listdir(folder_path)
    # 筛选出以.png 结尾的文件
    png_files = [file for file in all_files if file.endswith('.png')]
    # 拼接文件名称和路径
    png_path_list = [os.path.join(folder_path, file) for file in png_files]
    return png_path_list

def get_image_dict1(png_path):
    contents_temp = []
    print(png_path)
    base64_png = encode_image(png_path)
    content = {
        "type": "image_url",
        "image_url": {"url": f"data:image/jpg;base64,{base64_png}"},
    }
    contents_temp.append(content)
    return contents_temp

def get_image_dict(png_paths, index, batch_size):
    contents_temp = []
    for png_path in png_paths[index:index+batch_size]:
        print(png_path)
        base64_png = encode_image(png_path)
        content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpg;base64,{base64_png}"},
        }
        contents_temp.append(content)
    return contents_temp

def write_answer_to_file(result_file_name, ans, is_first):
    dir_name = os.path.dirname(result_file_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    mode = 'w' if is_first else 'a'
    with open(result_file_name, mode) as file:
        file.write(ans + '\n')

def write_answer_to_file1(result_file_name, image_path, coordinates, is_first=False):
    """ 追加写入文件，以 `图片路径: [(x1, y1), (x2, y2), ...]` 格式存储 """
    # 确保目录存在
    dir_name = os.path.dirname(result_file_name)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    mode = 'w' if is_first else 'a'  # `is_first=True` 时覆盖，`False` 时追加
    with open(result_file_name, mode, encoding='utf-8') as file:
        # 格式化字符串："图片路径: [(x1, y1), (x2, y2), ...]"
        formatted_text = f"{image_path}: {coordinates}\n"
        file.write(formatted_text)

def write_answer_to_files2(file_path, input_image_path, coordinates, is_first=True):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    mode = 'w' if is_first else 'a'  # 追加模式
    with open(file_path, mode) as f:
        f.write(f"{input_image_path}: {coordinates}\n")


def write_answer_to_file1(file_path, input_image_path, coordinates, is_first=True):
    mode = 'w' if is_first else 'a'  # 追加模式
    with open(file_path, mode) as f:
        f.write(f"{input_image_path}: {coordinates}\n")


def extract_color_from_filename(filename):
    # valid_colors = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral', 'blueyellow']
    valid_colors = ['gray', 'Blues', 'hot', 'cubehelix', 'magma', 'coolwarm', 'rainbow', 'spectral','blueyellow']
    parts = filename.split('_')
    for part in parts:
        if part in valid_colors:
            return part

def combine_image_color(image_list, color_string):

    color_list = eval(color_string)
    result = ""
    for i in range(len(image_list)):
        if i < len(color_list):
            result += f"{image_list[i]}:{color_list[i]}\n"
        else:
            # 如果颜色列表长度小于图像列表长度，用 None 填充
            result += f"{image_list[i]}:None\n"
    return result


def combine_image_color1(image_list, color_string):
    # 正确分组匹配每一个独立的 [[...]] 块
    pattern = r"\[\[.*?\]\]"  # 非贪婪匹配 [[...]] 结构
    matches = re.findall(pattern, color_string)

    # 转换匹配的字符串为 Python 列表
    color_list = []
    for match in matches:
        try:
            # 安全解析为嵌套列表
            coords = eval(match)  # 如果有安全问题，可以替换成 `json.loads` 并预处理为 JSON 格式
            color_list.append(coords)
        except Exception as e:
            print(f"坐标解析失败: {match}, 错误: {e}")
            color_list.append([])  # 无法解析时填充空列表

    # 将坐标与图像对应
    result = []
    for i, image in enumerate(image_list):
        if i < len(color_list):
            coordinates = color_list[i]
            if coordinates:  # 坐标非空
                coord_str = ", ".join(f"({x}, {y})" for x, y in coordinates)
                result.append(f"{image}: [{coord_str}]")
            else:
                result.append(f"{image}: None")
        else:
            result.append(f"{image}: None")  # 如果坐标不足，补充 None

    # 返回结果字符串
    return "\n".join(result)


def combine_image_color2(image_list, color_list):
    result = ""
    for i in range(len(image_list)):
        if i < len(color_list):
            result += f"{image_list[i]}:{color_list[i]}\n"
        else:
            # If color_list is shorter than image_list, fill with None
            result += f"{image_list[i]}:None\n"
    return result

    # 将坐标与图像对应
    result = []
    for i, image in enumerate(image_list):
        if i < len(color_list):
            coordinates = color_list[i]
            if coordinates:  # 坐标非空
                coord_str = ", ".join(f"({x}, {y})" for x, y in coordinates)
                result.append(f"{image}: [{coord_str}]")
            else:
                result.append(f"{image}: None")
        else:
            result.append(f"{image}: None")  # 如果坐标不足，补充 None

    # 返回结果字符串
    return "\n".join(result)


def combine_image_color3(image_list, color_string):
    # 解析颜色数据：提取出“曲线X是正确的曲线”这类信息
    correct_curves = []
    lines = color_string.split('\n')
    for line in lines:
        if "曲线" in line:
            match = re.search(r"(曲线\d是正确的曲线)", line)
            if match:
                correct_curves.append(match.group(1))  # 直接存储完整的描述字符串

    # 生成图像和曲线的映射
    result = ""
    for i in range(len(image_list)):
        if i < len(correct_curves):
            result += f"{image_list[i]}:{correct_curves[i]}\n"  # 输出完整的曲线描述
        else:
            result += f"{image_list[i]}:None\n"
    return result


base_url, api_key = read_api_info_from_txt("api_info.txt")

client = OpenAI(base_url=base_url, api_key=api_key)
