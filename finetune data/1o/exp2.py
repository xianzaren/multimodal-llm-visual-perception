import json
import os
import gc
import re

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
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r"^(.*\.png)\s*:\s*(.+?) Box Avg$", line)
            if match:
                imgname = match.group(1)
                filename = re.sub(r'\.png$', '',imgname)
                ans=match.group(2)
                color =ans.lower()
                results[filename] = color
    return results

base_path = '../../../image_finetune/exp2_3/'
output_file = "finetune_exp2.jsonl"
id_counter = 0

if os.path.exists(output_file):
    os.remove(output_file)

def process_file(cm):
    global id_counter
    cm_path = os.path.join(base_path, cm)
    png_files = [f for f in os.listdir(cm_path) if f.endswith('.png')]

    res_path = os.path.join(cm_path, "result.txt")
    ans = parse_expected_results(res_path)

    for png_file in png_files:
        with open(output_file, 'a', encoding='utf-8') as f_out:

            image_filename = os.path.splitext(png_file)[0]
            image_path = os.path.join(f"exp2/{cm}", image_filename).replace("\\", "/")
            image_path2 = image_path+".png"

            conversation = [
                {
                    "from": "human",
                    "value": f"<image>\nCompare the steepness of terrain inside the two boxes, then choose the box that is steeper on average.Give me the box color."
                },
                {
                    "from": "gpt",
                    "value": f"[{ans[image_filename]}]"
                }
            ]
            record = {
                "id": id_counter,
                "image": image_path2,
                "conversations": conversation,
                "width": 915,
                "height": 578
            }
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"记录了{id_counter}条数据")
            id_counter += 1

    # del df
    # gc.collect()

for cm in colormap_list:
    process_file(cm)

print(f"数据集已成功保存为 {output_file}")
