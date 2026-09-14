from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from noise import pnoise2
import numpy as np
import os
import pandas as pd
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# 全局 DEM 数据尺寸
np.random.seed(42)
width, height = 967, 630

def generate_perlin_noise(width, height, scale, octaves, persistence, lacunarity, base):
    noise = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            noise[y][x] = pnoise2(
                x / scale,
                y / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=base
            )
    return noise

# 从 JSON 文件加载图片参数（每个数据包含两张图片，使用 without_border 作为 image_id）
with open('./static/Data/image_params.json', 'r', encoding='utf-8') as f:
    params_data = json.load(f)

# 构造映射字典，使用 without_border 作为图片标识
base_mapping = {item["without_border"]: item["base"] for item in params_data["images"]}

# 固定噪声参数
scale = 100.0
octaves = 5
persistence = 0.5
lacunarity = 2.0

# 构造全局字典，保存每个图片对应的 DEM 数据及真实数值
dem_data = {}
for item in params_data["images"]:
    image_id = item["without_border"]   # 使用 without_border 作为 key
    base_value = item["base"]
    noise = generate_perlin_noise(width, height, scale, octaves, persistence, lacunarity, base_value)
    normalized = (noise - noise.min()) / (noise.max() - noise.min()) * 1000
    dem_data[image_id] = {
        "normalized": normalized,
        "true_max": float(np.max(normalized)),
        "true_min": float(np.min(normalized)),
    }

# 用于记录用户数据
results = []

# 接口：根据点击坐标返回 csv 数据（同时传入 image_id 参数）
@app.route('/query_value')
def query_value():
    image_id = request.args.get('image_id', type=str)
    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)
    experiment_index = int(request.args.get('experiment_index', 0))

    if not image_id:
        return jsonify({'error': 'Invalid image_id'}), 400

    csv_index = experiment_index % len(csv_files)
    csv_path = csv_files[csv_index]

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return jsonify({'error': 'CSV file not found'}), 500

    try:
        df = pd.read_csv(csv_path, header=None, skiprows=1, sep=",")
        height, width = df.shape

        print(f"📊 CSV Shape: width={width}, height={height}")
        print(f"🔍 请求坐标: (x={x}, y={y})")

        if x >= width or y >= height:
            print(f"❌ 超出范围: (x={x}, y={y}) 超过 (max_x={width-1}, max_y={height-1})")
            return jsonify({'error': 'Coordinates exceed CSV bounds'}), 400

        value_at_coord = df.iloc[y, x]
        print(f"✅ CSV: {csv_path} - (x={x}, y={y}) -> Found Value: {value_at_coord}")
        return jsonify({'x': x, 'y': y, 'value': float(value_at_coord), 'csv_file': csv_path})

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return jsonify({'error': 'Error reading CSV'}), 500

# 添加色盲检测页面路由
@app.route('/color_test', methods=['GET', 'POST'])
def color_test():
    # 正确答案样例：请根据实际情况调整
    correct_answers = {
        "img1": "36",
        "img2": "9",
        "img3": "3",
        "img4": "45",
        "img5": "26",
        "img6": "6"
    }
    if request.method == 'POST':
        # 收集所有答案
        answers = {}
        for i in range(1, 7):
            answers[f"img{i}"] = request.form.get(f'ans{i}', '').strip()
        # 检查所有答案是否正确
        if all(answers[f"img{i}"] == correct_answers[f"img{i}"] for i in range(1, 7)):
            return redirect(url_for('login'))
        else:
            flash("Color vision test failed, please try again.", "danger")
            return render_template('colorblind.html')
    else:
        return render_template('colorblind.html')

# 首页: 展示实验简介
@app.route('/')
def intro():
    return render_template('intro.html')

# 登陆页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', 'Anonymous')
        age = request.form.get('age')
        gender = request.form.get('gender')
        # 新增字段：专业
        major = request.form.get('major', '')
        monitor = request.form.get('monitor', '')
        # 后续传递用户信息到实验页面
        return redirect(url_for('experiment', username=username, age=age, gender=gender, major=major, monitor=monitor))
    return render_template('login.html')

# 定义 5 个 CSV 文件路径
csv_files = [
    "./static/Data/data1.csv",
    "./static/Data/data2.csv",
    "./static/Data/data3.csv",
    "./static/Data/data4.csv",
    "./static/Data/data5.csv"
]
# 记录实验数据
result = []
@app.route('/experiment', methods=['GET', 'POST'])
def experiment():
    username = request.args.get('username', 'Anonymous')
    major = request.args.get('major', '')

    # ✅ 确保从 URL 解析 experiment_index
    try:
        experiment_index = int(request.args.get('experiment_index', 0))
    except ValueError:
        experiment_index = 0  # 解析失败时默认 0

    print(f"🟢 Experiment Index (GET): {experiment_index}")  # ✅ 确认 experiment_index 递增

    if request.method == 'POST':
        print("✅ Received POST request for experiment")
        try:
            # ✅ 确保从 POST 获取 experiment_index
            experiment_index = int(request.form.get('experiment_index', experiment_index))
            print(f"🟢 Experiment Index (POST): {experiment_index}")

            image_id = request.form.get('image_id', '')
            print(f"🔍 Image ID: {image_id}")
            if not image_id:
                return "Error: Missing image_id"

            # **计算正确的 csv_index**
            csv_index = experiment_index % len(csv_files)  # ✅ 计算正确的索引
            csv_path = csv_files[csv_index]
            print(f"📂 /experiment 选取的 CSV: {csv_path}")  # ✅ 确保选取正确的 CSV

            if not os.path.exists(csv_path):
                print(f"❌ CSV file not found: {csv_path}")
                return jsonify({'error': 'CSV file not found'}), 500

            # **读取 CSV**
            df = pd.read_csv(csv_path, header=None, skiprows=1, sep=",")
            df = df.astype(float)

            # **解析点击坐标**
            points = []
            for i in range(1, 6):
                x = request.form.get(f'{i}_x')
                y = request.form.get(f'{i}_y')
                if x is None or y is None or x == "null" or y == "null":
                    print(f"❌ Missing coordinates for point {i}: x={x}, y={y}")
                    return f"Error: Missing coordinates for point {i}"
                x, y = int(x), int(y)
                points.append((x, y))

            print("🟢 Clicked Points:", points)

            # **获取真实值**
            true_values = []
            for x, y in points:
                if x >= df.shape[1] or y >= df.shape[0]:  # 避免超出范围
                    print(f"❌ 坐标超界: (x={x}, y={y}) 超过 (max_x={df.shape[1] - 1}, max_y={df.shape[0] - 1})")
                    true_values.append(None)
                else:
                    value = df.iloc[y, x]
                    print(f"✅ /experiment 获取值: (x={x}, y={y}) -> {value}")  # 确保取值正确
                    true_values.append(value)

            print("🟢 /experiment True Values from CSV:", true_values)  # 确认数值

            # **存入 Excel**
            file_path = './static/Data/result.xlsx'
            df_new = pd.DataFrame([{
                'username': username,
                'major': major,
                'experiment_index': experiment_index,
                'image_id': image_id,
                'csv_file': csv_path,  # ✅ 记录使用的 CSV 文件
                'user_points': points,
                'true_values': true_values
            }])

            # **追加到已有数据**
            if os.path.exists(file_path):
                try:
                    df_existing = pd.read_excel(file_path)  # **读取已有数据**
                    df_final = pd.concat([df_existing, df_new], ignore_index=True)  # **合并数据**
                except Exception as e:
                    print(f"❌ 读取 Excel 失败: {e}")
                    df_final = df_new
            else:
                df_final = df_new

            # **保存 Excel**
            try:
                df_final.to_excel(file_path, index=False, engine='xlsxwriter')
                print(f"✅ 数据成功保存到 {file_path}: Experiment {experiment_index}")
            except Exception as e:
                print(f"❌ 写入 Excel 失败: {e}")

            # **跳转到下一个实验**
            return redirect(url_for('experiment', experiment_index=experiment_index + 1))

        except Exception as e:
            print(f"❌ Error in /experiment: {e}")
            return f"Error in experiment: {e}"

    return render_template(
        'experiment.html',
        username=username,
        experiment_index=experiment_index,
        image_id=params_data["images"][experiment_index]["without_border"]
    )


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

if __name__ == '__main__':
    app.run(debug=True)