import pandas as pd
import os

# 示例数据和参数
coords = [
    (450, 310),  # 假设1.0的点
    (380, 290),  # 假设0.8的点
    (300, 260),  # 假设0.6的点
    (240, 210),  # 假设0.4的点
    (190, 160),   # 假设0.2的点
]

weight_values = [1.0, 0.8, 0.6, 0.4, 0.2]  # 权重值对应于坐标

csv_base_path = "../../data/uncolor"
shape = '(630, 820)'
csv_path = os.path.abspath(fr"{csv_base_path}/Noise_{shape}_(7, 7)_5.csv")

# 加载 CSV 文件（跳过第一行）
try:
    df = pd.read_csv(csv_path, header=None, skiprows=1)
except Exception as e:
    print(f"Error: Fail to load CSV - {csv_path} | {e}")
    raise  # 重新抛出异常，结束程序

# 遍历坐标并生成结果
for weight, (x_str, y_str) in zip(weight_values, coords):
    x, y = int(x_str), int(y_str)  # 转换为整数
    if x < 0 or x >= len(df.columns) or y < 0 or y >= len(df):
        print(f"{weight}: ({x}, {y}) - OutOfRange")
    else:
        value_at_coord = df.iloc[len(df) - y - 1, x]  # 获取对应的值
        print(f"{weight}: ({x}, {y}) - [{value_at_coord}]")
