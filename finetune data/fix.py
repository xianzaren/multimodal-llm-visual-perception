'''import re

def fix_file_format(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    fixed_lines = []
    for line in lines:
        # 使用正则表达式修正文件名格式
        fixed_line = re.sub(r'(_\d+)\.png_(\d+)(:)', r'\1_\2.png\3', line)  # 修正文件名格式
        fixed_lines.append(fixed_line)

    # 将修复后的内容写入到新的文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)

colormap_list = [
    'gray', 'blues', 'hot', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]

for colormap in colormap_list:
    # 使用修复函数修正 result.txt 文件
    input_file_path = f'images/nexp2/{colormap}/result.txt'  # 替换为您的 result.txt 文件路径
    output_file_path = f'images/nexp2/{colormap}/fixresult.txt'  # 替换为您想写入的新的文件路径
    input_file_path = f'../color/exp2/{colormap}/result.txt'  # 替换为您的 result.txt 文件路径
    output_file_path = f'../color/exp2/{colormap}/fixresult.txt'  # 替换为您想写入的新的文件路径
    fix_file_format(input_file_path, output_file_path)'''
import re

def fix_file_format(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    fixed_lines = []
    for line in lines:
        # 使用正则表达式修复文件名格式
        # 将 .png_1 格式修复为 _1.png
        fixed_line = re.sub(r'(\.png)_(\d+)', r'_\2\1', line)  # 将 _数字 移到 .png 前
        fixed_lines.append(fixed_line)

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.writelines(fixed_lines)

colormap_list = [
    'gray', 'blues', 'hot', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]

for colormap in colormap_list:
    # 使用修复函数修正 result.txt 文件
    input_file_path = f'../color/exp2/{colormap}/result.txt'  # 替换为您的 result.txt 文件路径
    output_file_path = f'../color/exp2/{colormap}/fixresult.txt'  # 替换为您想写入的新的文件路径
    fix_file_format(input_file_path, output_file_path)


