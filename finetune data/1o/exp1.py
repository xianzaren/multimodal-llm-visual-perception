import json
import os
import pandas as pd
import gc

# 基础路径和 CSV 文件列表（注意：CSV 文件包含标题行）
base_path = '../../../image_finetune/exp1_1/'
file_names = [
    "exp1_scalar_field_f1.csv",
    "exp1_scalar_field_f2.csv",
    "exp1_scalar_field_f3.csv",
    "exp1_scalar_field_f4.csv",
    "exp1_scalar_field_f5.csv",
]

# 9 种 colormap 名称
colormap_list = [
    'greyscale', 'singlehue', 'bodyheat', 'cubehelix', 'extbodyheat',
    'coolwarm', 'rainbow', 'spectral', 'blueyellow'
]

# 图片存放路径
images_path = "../../image_finetune/exp1_1/"

output_file = "../create_datasets/finetune_exp1_448.jsonl"
id_counter = 0


def format_coord(coord):
    """将坐标元组转换为 JSON 数组格式"""
    return f'[{coord[0]}, {coord[1]}]'


if os.path.exists(output_file):
    os.remove(output_file)


def process_file(file_name, cm):
    print(f"===============================================正在遍历{file_name}")
    global id_counter
    file_path = os.path.join(base_path, file_name)
    # 假设高度值为 1 到 1000（若需要包含 0，可调整为 range(0, 1001)）
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, header=0)
        total_rows, total_cols = df.shape
        parts = file_name.split('_')
        f_value = parts[3][1]

        with open(output_file, 'a', encoding='utf-8') as f_out:
            flag = {height: 0 for height in range(0, 1001)}
            print(f"********************************************colormap为{cm}")
            # print(total_rows)
            # print(total_cols)
            for r in range(total_rows - 1, -1, -1):
                y_coord = total_rows - 1 - r # y 0-630
                for c in range(total_cols):   # c 0-830
                    x_coord = c  # 列即 x 坐标
                    coord = (x_coord, y_coord)
                    coord_str = format_coord(coord)
                    height_find = int(df.iat[r, c])
                    if flag[height_find] >=6 :
                        continue

                    flag[height_find] += 1
                    print(f"记录了{id_counter}条")

                    image_filename = f"f{f_value}_{cm}.png"
                    # 图片路径： images_path/colormap/图片文件名
                    image_path = os.path.join(f"exp1_1/{cm}", image_filename).replace("\\", "/")

                    conversation = [
                        {
                            "from": "human",
                            "value": f"<image>\nFind the coordinate of the point with the value {height_find} in the scalar field image."
                        },
                        {
                            "from": "gpt",
                            "value": coord_str
                        }
                    ]
                    record = {
                        "id": id_counter,
                        "image": image_path,
                        "conversations": conversation,
                        "width": 448,
                        "height": 448
                    }
                    f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                    id_counter += 1

    # 内存清理
    del df
    gc.collect()


# 遍历所有 CSV 文件
for file_name in file_names:
    for cm in colormap_list:
        process_file(file_name, cm)

print(f"数据集已成功保存为 {output_file}")
