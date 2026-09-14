import os
import re
import pandas as pd

folder = 'check'
# 设置文件夹路径（包含所有 TXT 文件的文件夹）
base_folder = f'../../result/{folder}'  # 主文件夹路径
#color_types = ['greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow',
 #                            'spectral', 'blueyellow']
color_types = ['gray', 'Blues', 'hot', 'cubehelix', 'magma', 'coolwarm', 'rainbow',
                             'spectral', 'blueyellow']

# 正则表达式模式，用于提取行中的实际值和预测值
pattern = re.compile(r'(\d*\.\d+):\s*\(\d+, \d+\)\s*-\s*\[(\d*\.?\d*)\]')  # 提取实际值和预测值
print()
# 用于存储每种 colormap 的差值数据
csv_data = {color: {} for color in color_types}

# 遍历每个文件夹
for i in range(1, 11):  # 假设有 30 个文件夹
    folder_path = os.path.join(base_folder, str(i))

    # 存储每个文件夹内的所有文件类型的差值数据
    folder_values = {color: [] for color in color_types}

    for color in color_types:
        txt_file_path = os.path.join(folder_path, f'{color}_result.txt')

        if os.path.exists(txt_file_path):  # 仅处理存在的文件
            with open(txt_file_path, 'r', encoding='utf-8') as file:
                content = file.readlines()  # 读取所有行
                extracted_values = []

                # 提取每行中的实际值和预测值，并计算它们的差值
                for line in content:
                    match = pattern.search(line)  # 查找符合模式的数值
                    if match:
                        actual_value = float(match.group(1))  # 实际值
                        predicted_value = float(match.group(2))  # 预测值
                        diff = abs(actual_value - predicted_value)  # 计算差值的绝对值
                        print(actual_value,predicted_value)
                        extracted_values.append(diff)
                    else:
                        extracted_values.append('')  # 如果没有匹配到，填充空值

                # 将提取的值添加到对应的文件夹类型的列表中
                folder_values[color].extend(extracted_values)

    # 将当前文件夹的结果按文件夹编号存储到 csv_data 字典中
    for color in color_types:
        if folder_values[color]:  # 仅记录存在数据的 colormap
            csv_data[color][f'Folder {i}'] = folder_values[color]

# 确保输出文件夹存在
output_folder = f'../../result/{folder}/data'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 将所有 colormap 的数据保存到一个 Excel 文件的不同 sheet 中
excel_filename = os.path.join(output_folder, 'colormap_diff_results.xlsx')
with pd.ExcelWriter(excel_filename) as writer:
    for color in color_types:
        # 如果该 colormap 有数据，则保存到对应的 sheet
        if csv_data[color]:
            # 找出所有数据的最大长度，用于对齐列数
            max_length = max(len(data) for data in csv_data[color].values())
            # 填充数据以对齐列数
            data_padded = {
                folder: values + [''] * (max_length - len(values))
                for folder, values in csv_data[color].items()
            }
            # 构造 DataFrame
            df = pd.DataFrame(data_padded)
            # 写入到 Excel 的对应 sheet
            df.to_excel(writer, sheet_name=color, index=False)
            print(f"✅ 已将 {color} 的差值数据保存到 {excel_filename} 的 {color} sheet")

print(f"✅ 所有 colormap 差值数据已保存到 {excel_filename}")
