import os
import re
import pandas as pd
from collections import defaultdict

# 期望结果文件路径
filename = 'result.txt'

expected_files = {
    "gray": fr"../../color/oringinal test/texp2/gray/{filename}",
    "hot": fr"../../color/oringinal test/texp2/hot/{filename}",
    "rainbow": fr"../../color/oringinal test/texp2/rainbow/{filename}",
    "Blues": fr"../../color/oringinal test/texp2/Blues/{filename}",
    "blueyellow": fr"../../color/oringinal test/texp2/blueyellow/{filename}",
    "spectral": fr"../../color/oringinal test/texp2/spectral/{filename}",
    "magma": fr"../../color/oringinal test/texp2/magma/{filename}",
    "cubehelix": fr"../../color/oringinal test/texp2/cubehelix/{filename}",
    "coolwarm": fr"../../color/oringinal test/texp2/coolwarm/{filename}"
}

def parse_expected_results(file_path):
    """解析单个期望结果文件，提取名称和颜色结果"""
    results = {}
    if not os.path.exists(file_path):
        print(f"❌ 期望结果文件未找到: {file_path}")
        return results  # 返回空字典
    print(f"\n📂 读取期望结果文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r"ScalarField_WithBoxes_Noise_(.*)\.png: (\w+ Box Avg)", line)
            if match:
                filename = match.group(1)  # 提取文件名
                color = match.group(2).split()[0].lower()  # 提取颜色信息
                results[filename] = color
    return results


def parse_actual_results(file_path):
    """解析实际结果文件，提取名称和颜色结果"""
    results = {}
    if not os.path.exists(file_path):
        print(f"❌ 实验结果文件未找到: {file_path}")
        return results  # 返回空字典
    print(f"\n📂 读取实验结果文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        for line in file:
            match = re.match(r".*Noise_((\(\d+, \d+\)_\(\d+, \d+\)_\d+_\w+_\d+))\.png:(\w+)", line)
            if match:
                filename = match.group(1)
                color = match.group(3).lower()
                results[filename] = color
    return results


def calculate_accuracy(actual_results, expected_results):
    """计算实验结果的正确率，并返回文件级的正确性"""
    correct = 0
    total = 0
    file_accuracy_data = []  # 用于记录每个文件的详细信息
    for filename, expected_label in expected_results.items():
        if filename in actual_results:
            total += 1
            actual_label = actual_results[filename]
            is_correct = actual_label == expected_label
            file_accuracy_data.append({
                "File": filename,
                "Expected Color": expected_label,
                "Actual Color": actual_label,
                "Correct": is_correct
            })
            if is_correct:
                correct += 1
    accuracy = (correct / total) * 100 if total > 0 else 0
    return accuracy, file_accuracy_data


def calculate_frequency_accuracy(actual_results, expected_results):
    """计算每个colormap的不同频率（坐标对）下的平均准确率"""
    frequency_accuracy_data = defaultdict(lambda: defaultdict(list))  # {colormap: {frequency: [accuracies]}}

    for filename, expected_label in expected_results.items():
        if filename in actual_results:
            actual_label = actual_results[filename]
            # 提取频率（例如 (1, 1)）
            match = re.search(r"\((\d+), (\d+)\)_\((\d+), (\d+)\)", filename)
            if match:
                frequency = f"({match.group(3)}, {match.group(4)})"  # 取第二组和第四组作为频率
                is_correct = actual_label == expected_label
                frequency_accuracy_data[expected_label][frequency].append(1 if is_correct else 0)

    # 计算每个colormap下的频率准确率
    frequency_avg_accuracy_data = []
    for colormap, frequencies in frequency_accuracy_data.items():
        for frequency, accuracies in frequencies.items():
            avg_accuracy = (sum(accuracies) / len(accuracies)) * 100 if accuracies else 0
            frequency_avg_accuracy_data.append({
                "Colormap": colormap,
                "Frequency": frequency,
                "Average Accuracy": avg_accuracy
            })

    return frequency_avg_accuracy_data


# 解析所有期望结果
expected_results = {colormap: parse_expected_results(path) for colormap, path in expected_files.items()}

# 存储所有用户的准确率
all_users_data = []
file_level_data = []  # 用于记录文件级别的详细数据
file_avg_accuracy = {}  # 用于记录每个文件的平均准确率
folder = 'exp2'
for i in range(1, 11):  # 受试者编号 1~30
    print(f"\n📌 受试者 {i} 的实验文件路径:")
    user_folder = f"../../result/{folder}/{i}/"
    if not os.path.exists(user_folder):
        print(f"❌ 受试者 {i} 的实验文件夹不存在: {user_folder}")
        continue

    # 获取存在的 colormap 文件
    available_colormaps = [f.split(".txt")[0] for f in os.listdir(user_folder) if f.endswith(".txt")]
    for colormap in available_colormaps:
        if colormap not in expected_results:
            continue

        path = os.path.join(user_folder, f"{colormap}.txt")
        print(f"  - {colormap}: {path}")

        # 解析实际实验数据
        actual_results = parse_actual_results(path)
        # 计算准确率和文件级别数据
        accuracy, file_accuracy = calculate_accuracy(actual_results, expected_results[colormap])

        # 记录用户级别的准确率
        all_users_data.append({"User": i, "Colormap": colormap, "Accuracy": accuracy})

        # 记录文件级别的详细信息
        for entry in file_accuracy:
            entry["User"] = i
            entry["Colormap"] = colormap
            file_level_data.append(entry)

            # 记录每个文件的准确率
            file_name = entry["File"]
            if file_name not in file_avg_accuracy:
                file_avg_accuracy[file_name] = []
            file_avg_accuracy[file_name].append(1 if entry["Correct"] else 0)

# 计算每个文件的平均准确率
file_avg_accuracy_data = []
for file_name, accuracies in file_avg_accuracy.items():
    avg_accuracy = (sum(accuracies) / len(accuracies)) * 100 if accuracies else 0
    file_avg_accuracy_data.append({"File": file_name, "Average Accuracy": avg_accuracy})

# 计算每个colormap下不同频率的平均准确率
frequency_avg_accuracy_data = []
for i in range(1, 11):  # 受试者编号 1~30
    print(f"\n📌 受试者 {i} 的实验文件路径:")
    user_folder = f"../../result/{folder}/{i}/"
    if not os.path.exists(user_folder):
        print(f"❌ 受试者 {i} 的实验文件夹不存在: {user_folder}")
        continue

    # 获取存在的 colormap 文件
    available_colormaps = [f.split(".txt")[0] for f in os.listdir(user_folder) if f.endswith(".txt")]
    for colormap in available_colormaps:
        if colormap not in expected_results:
            continue

        path = os.path.join(user_folder, f"{colormap}.txt")
        print(f"  - {colormap}: {path}")

        # 解析实际实验数据
        actual_results = parse_actual_results(path)

        # 计算频率准确率
        frequency_avg_accuracy_data.extend(calculate_frequency_accuracy(actual_results, expected_results[colormap]))

# 保存Excel报告
accuracy_report_path = os.path.join(f"../../result/{folder}/", "accuracy_report_with_frequency.xlsx")
df_all_users = pd.DataFrame(all_users_data)
df_file_level = pd.DataFrame(file_level_data)
df_file_avg = pd.DataFrame(file_avg_accuracy_data)
df_frequency_avg = pd.DataFrame(frequency_avg_accuracy_data)

with pd.ExcelWriter(accuracy_report_path) as writer:
    # 保存所有用户数据
    df_all_users.to_excel(writer, sheet_name="All_Users_Accuracy", index=False)
    # 保存文件级别的数据
    df_file_level.to_excel(writer, sheet_name="File_Level_Accuracy", index=False)
    # 保存每个文件的平均准确率
    df_file_avg.to_excel(writer, sheet_name="File_Avg_Accuracy", index=False)
    # 保存每个colormap频率的平均准确率
    df_frequency_avg.to_excel(writer, sheet_name="Frequency_Avg_Accuracy", index=False)

print(f"\n📊 数据报告已保存至: {accuracy_report_path}")
