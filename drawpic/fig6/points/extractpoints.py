import os
import re

def extract_first_line_of_coolwarm_txt(src_dir, output_file):
    # 确保目标文件夹存在
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 创建文件夹

    # 打开输出文件，准备写入
    with open(output_file, 'w') as outfile:
        # 遍历文件夹及其子文件夹
        for root, dirs, files in os.walk(src_dir):
            # 查找名为 coolwarm.txt 的文件
            if 'coolwarm.txt' in files:
                file_path = os.path.join(root, 'coolwarm.txt')
                with open(file_path, 'r') as infile:
                    # 读取第一行
                    first_line = infile.readline().strip()
                    # 将第一行写入到输出文件
                    outfile.write(first_line + '\n')


def extract_coordinates_from_txt(src_dir):
    # 遍历文件夹中的所有文件
    for filename in os.listdir(src_dir):
        if filename.endswith(".txt"):  # 确保只处理txt文件
            file_path = os.path.join(src_dir, filename)
            # 读取文件
            with open(file_path, 'r') as infile:
                lines = infile.readlines()
            # 创建 value 文件夹（如果不存在）
            value_dir = os.path.join(src_dir, 'value')
            if not os.path.exists(value_dir):
                os.makedirs(value_dir)
            # 创建输出文件，命名为原文件名_points.txt，并保存在 value 文件夹中
            output_file = os.path.join(value_dir, f"{os.path.splitext(filename)[0]}_points.txt")
            with open(output_file, 'w') as outfile:
                for line in lines:
                    # 使用正则表达式提取所有括号中的坐标
                    matches = re.findall(r"\((\d+), (\d+)\)", line)
                    if len(matches) > 1:  # 确保存在至少两个括号
                        # 提取第二个括号中的坐标
                        second_coord = matches[1]
                        outfile.write(f"({second_coord[0]}, {second_coord[1]})\n")
# 使用示例
type = 'oringin'
prompt = 'baseline'
modellist = ['8b_GT']
for model in modellist:
    source_directory = fr'../data/{type} {prompt}/{model}'  # 替换为实际文件夹路径
    output_txt_file = fr'value/{type}_{prompt}_{model}.txt'      # 替换为目标输出文件路径
    extract_first_line_of_coolwarm_txt(source_directory, output_txt_file)
# 使用示例
source_directory = 'points'  # 替换为实际的文件夹路径
extract_coordinates_from_txt(source_directory)
