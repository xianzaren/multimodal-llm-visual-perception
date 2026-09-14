import json
import os
import pandas as pd
import gc
import base64
from PIL import Image
from io import BytesIO

# 基础路径和 CSV 文件列表（注意：CSV 文件包含标题行）
base_path = 'images/exp1'
file_names = [
    "exp1_scalar_field_f1.csv",
    "exp1_scalar_field_f2.csv",
    "exp1_scalar_field_f3.csv",
    "exp1_scalar_field_f4.csv",
    "exp1_scalar_field_f5.csv",
]

colormap_list = ['blueyellow']

# 9 种 colormap 名称
'''colormap_list = [
    'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]'''

# 图片存放路径
images_path = "images/exp1"

output_file = "dataset/finetune_exp1.jsonl"
id_counter = 0

def format_coord(coord):
    """将坐标元组转换为 JSON 数组格式"""
    return f'[{coord[0]}, {coord[1]}]'

if os.path.exists(output_file):
    os.remove(output_file)


def process_file(file_name, cm):
    print(f"===============================================正在遍历 {file_name}，colormap：{cm}")
    global id_counter
    file_path = os.path.join(base_path, file_name)
    # 假设高度值为 0 到 1000（若需要调整范围，可修改 range(0, 1001)）
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, header=0)
        total_rows, total_cols = df.shape
        parts = file_name.split('_')
        f_value = parts[3][1]  # 从 "f1.csv" 中提取数字 1

        with open(output_file, 'a', encoding='utf-8') as f_out:
            flag = {height: 0 for height in range(0, 1001)}
            for r in range(total_rows - 1, -1, -1):
                y_coord = total_rows - 1 - r  # 计算 y 坐标（从 0 开始）
                for c in range(total_cols):
                    x_coord = c  # x 坐标即为列号
                    coord = (x_coord, y_coord)
                    coord_str = format_coord(coord)
                    height_find = int(df.iat[r, c])
                    if flag[height_find] >= 6:
                        continue
                    flag[height_find] += 1
                    print(f"记录了 {id_counter} 条，height: {height_find}")

                    # 构造图片文件名，例如 "f1_greyscale.png"
                    image_filename = f"f{f_value}_{cm}.png"
                    # 构造图片完整路径： images_path/colormap/图片文件名
                    full_image_path = os.path.join(images_path, cm, image_filename)
                    # 将路径转换为统一的正斜杠格式（仅用于调试或记录，如有需要）
                    posix_image_path = full_image_path.replace("\\", "/")

                    # 构造对话 JSON 格式
                    baselineprompt = f"Find the coordinate of the point with the value {height_find} in the scalar field image."
                    json_data = {
                        "messages": [
                            {"role": "system", "content": "You are an assistant that identifies uncommon cheeses."},
                            {"role": "user", "content": baselineprompt},
                            {"role": "user", "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"http://sti6nanlq.hn-bkt.clouddn.com/exp1/{cm}/{image_filename}"
                                    }
                                }
                            ]},
                            {"role": "assistant", "content": coord_str}
                        ]
                    }

                    # 写入 JSONL 文件
                    f_out.write(json.dumps(json_data, ensure_ascii=False) + "\n")
                    id_counter += 1
        # 内存清理（仅当 df 存在时调用）
        del df
        gc.collect()
    else:
        print(f"文件 {file_path} 不存在，跳过。")


# 遍历所有 CSV 文件和所有 colormap
for file_name in file_names:
    for cm in colormap_list:
        process_file(file_name, cm)

print(f"数据集已成功保存为 {output_file}")
