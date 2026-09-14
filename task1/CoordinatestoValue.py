import os
import re
import pandas as pd


def clean_zero_width_spaces(text):
    """清除零宽字符"""
    return re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)


def process_coordinates(txt_file, csv_mapping, output_txt, log_file):
    if not os.path.exists(txt_file):
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Error: Coordinate file not found - {txt_file}\n")
        print(f"❌ Error: Coordinate file not found - {txt_file}")
        return

    with open(txt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    all_results = []  # 保存所有处理结果
    weight_values = [1000, 750, 500, 250, 0]  # 权重值

    for line in lines:
        line = line.strip()
        line = clean_zero_width_spaces(line)  # 清除可能存在的零宽字符
        # 使用正则解析路径和坐标列表
        match = re.match(r'^(.*?):\s*\[(.*)\]$', line)
        if not match:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Error: Unable to parse line - {line}\n")
            continue

        img_path, coords_str = match.groups()
        coords = re.findall(r'[\[\(](\d+),\s*(\d+)[\]\)]', coords_str)
        if not coords or len(coords) != len(weight_values):
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Error: Invalid number of coordinates in line - {line}\n")
            continue

        # 提取 CSV 文件路径
        match_key = re.search(r'\(\d+, \d+\)_\((\d+), \d+\)', img_path)
        if not match_key:
            all_results.append(f"{img_path} - Invalid format")
            continue
        image_key = match_key.group(1)  # 提取第一个数字作为键
        csv_path = csv_mapping.get(image_key)
        if not csv_path or not os.path.exists(csv_path):
            for weight, coord in zip(weight_values, coords):
                all_results.append(f"{weight}: {coord} - CSV Not Found")
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Error: CSV file not found for key {image_key} - {csv_path}\n")
            continue

        try:
            # 加载 CSV 文件 (跳过第一行)
            df = pd.read_csv(csv_path, header=None, skiprows=1)
        except Exception as e:
            with open(log_file, 'a', encoding='utf-8') as log:
                log.write(f"Error: Fail to load CSV - {csv_path} | {e}\n")
            continue

        # 遍历坐标并生成结果
        img_results = []
        for weight, (x_str, y_str) in zip(weight_values, coords):
            x, y = int(x_str), int(y_str)
            if x < 0 or x >= len(df.columns) or y < 0 or y >= len(df):
                img_results.append(f"{weight}: ({x}, {y}) - OutOfRange")
                print(f"{weight}: ({x}, {y}) - OutOfRange")
            else:
                value_at_coord = df.iloc[y, x]#注意xy
                img_results.append(f"{weight}: ({x}, {y}) - [{value_at_coord}]")

        # 添加分段结果
        all_results.extend(img_results)
        all_results.append("")  # 空行分割不同图片

    # 将结果写入输出文件
    with open(output_txt, 'w', encoding='utf-8') as f:
        for line_out in all_results:
            f.write(line_out + "\n")

    print(f"✅ Processed {txt_file}, results saved to {output_txt}")


def check_and_write_empty_message(output_txt):
    """
    检查指定的输出文件是否为空，若为空则提示。
    """
    if os.path.exists(output_txt) and os.path.getsize(output_txt) == 0:
        print(f"⚠️ Warning: Output file is empty - {output_txt}")


def main():
    foldername = 'check'
    # 定义 CSV 文件的路径
    csv_base_path = "../../data/uncolor"
    shape = '(630, 820)'
    csv_mapping = {
        '1': os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(1, 1)_5.csv"),
        '3': os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(3, 3)_5.csv"),
        '5': os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(5, 5)_5.csv"),
        '7': os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(7, 7)_5.csv"),
        '9': os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(9, 9)_5.csv"),
    }
    # 日志文件路径
    log_file = os.path.abspath(r"../../error_log.txt")
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write("Error Log\n")
    for subfolder in range(1, 11):
        colormap_list = ['gray', 'Blues', 'hot', 'cubehelix', 'extbodyheat', 'coolwarm', 'rainbow', 'spectral', 'blueyellow']
        for colormap in colormap_list:
            base_dir = os.path.abspath(f"../../result/{foldername}/{subfolder}")  # 每个文件夹的基目录
            if not os.path.exists(base_dir):
                print(f"⚠️ 文件夹不存在: {base_dir}")
                continue
            # 遍历 colormap_list，检查哪些文件存在
            for colormap in colormap_list:
                input_file = os.path.join(base_dir, f"{colormap}.txt")  # 输入文件路径
                result_file = os.path.join(base_dir, f"{colormap}_result.txt")  # 输出文件路径
                # 如果文件存在，则处理
                if os.path.exists(input_file):
                    print(f"🎯 正在处理: {input_file}")
                    process_coordinates(input_file, csv_mapping, result_file, log_file)  # 处理坐标数据
                    check_and_write_empty_message(result_file)  # 检查并写入空消息（如果需要）

if __name__ == "__main__":
    main()
