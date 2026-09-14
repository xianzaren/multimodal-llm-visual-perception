import json
import os
import gc
import re
import base64

colormap_list = [
    'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]


def parse_expected_results(file_path):
    results = {}
    if not os.path.exists(file_path):
        print(f"❌ 期望结果文件未找到: {file_path}")
        return results  # 返回空字典
    print(f"\n📂 读取期望结果文件: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):  # 添加行号，帮助调试
                try:
                    # 例如行内容：f1_greyscale_10.png + 真实曲线是第 4 条
                    match = re.match(r"(\w+)_(\w+)_(\d+)\.png\s\+\s真实曲线是第\s(\d+)\s条", line)
                    if match:
                        fre_name = match.group(1)
                        color_name = match.group(2)
                        num = match.group(3)
                        filename = f"{fre_name}_{color_name}_{num}"
                        curve_number = match.group(4)
                        results[filename] = curve_number
                    else:
                        print(f"⚠️ 无法匹配该行内容: {line.strip()}")
                except Exception as e:
                    print(f"❌ 处理第 {line_num} 行时出错: {e}")
    except Exception as e:
        print(f"❌ 打开文件时发生错误: {str(e)}")
    return results


def image_to_base64(image_path):
    """将图片转换为 Base64 编码"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


base_path = 'images/exp3/'
images_path = "images/exp3/"

output_file = "dataset/finetune_exp3.jsonl"
id_counter = 0

if os.path.exists(output_file):
    os.remove(output_file)

# 定义用户 prompt
baselineprompt = "<image>\n Imagine a line from A to B. Select the elevation profile below that most closely matches its slope."


def process_file(cm):
    global id_counter
    cm_path = os.path.join(base_path, cm)  # 当前 colormap 文件夹路径
    png_files = [f for f in os.listdir(cm_path) if f.endswith('.png')]

    res_path = os.path.join(cm_path, "result.txt")
    ans = parse_expected_results(res_path)

    for png_file in png_files:
        image_filename = os.path.splitext(png_file)[0]
        # 构造图片相对路径，如 "exp3/greyscale/f1_greyscale.png"
        image_path = os.path.join(f"images_path/{cm}", image_filename).replace("\\", "/") + ".png"
        # 构造图片完整路径用于 Base64 转换
        full_image_path = os.path.join(cm_path, png_file)
        base64_encoded_image = image_to_base64(full_image_path)

        # 构造期望结果字符串，若找不到则显示 "unknown"
        coord_str = f"[{ans.get(image_filename, 'unknown')}]"

        json_data = {
            "messages": [
                {"role": "system", "content": "You are an assistant that identifies uncommon cheeses."},
                {"role": "user", "content": baselineprompt},
                {"role": "user", "content": [
                    {
                        "type": "image_base64",
                        "image_base64": {
                            "data": base64_encoded_image
                        }
                    }
                ]},
                {"role": "assistant", "content": coord_str}
            ]
        }

        with open(output_file, 'a', encoding='utf-8') as f_out:
            f_out.write(json.dumps(json_data, ensure_ascii=False) + "\n")
        print(f"记录了 {id_counter} 条数据")
        id_counter += 1


for cm in colormap_list:
    process_file(cm)

print(f"数据集已成功保存为 {output_file}")
