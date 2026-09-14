import json
import os
import gc
import re
import base64

colormap_list = [
    'gray', 'blues', 'hot', 'cubehelix', 'extbodyheat',
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
                filename = re.sub(r'\.png$', '', imgname)
                ans = match.group(2)
                color = ans.lower()
                results[filename] = color
    return results

base_path = 'images/nexp2'
output_file = "dataset/file-GPT-finetune_exp2.jsonl"
id_counter = 0

if os.path.exists(output_file):
    os.remove(output_file)

# 定义用户 prompt（baselineprompt）
baselineprompt = "Compare the steepness of terrain inside the two boxes, then choose the box that is steeper on average. Give me the box color."


def process_file(cm):
    global id_counter
    cm_path = os.path.join(base_path, cm)
    png_files = [f for f in os.listdir(cm_path) if f.endswith('.png')]

    res_path = os.path.join(cm_path, "result.txt")
    ans = parse_expected_results(res_path)

    for png_file in png_files:
        image_filename = png_file

        # 使用解析得到的结果作为期望答案，若找不到则返回 'unknown'
        coord_str = f"[{ans.get(image_filename, 'unknown')}]"

        # 构造新的 JSON 格式
        json_data = {
            "messages": [
                {"role": "system", "content": "You are an assistant that identifies uncommon cheeses."},
                {"role": "user", "content": baselineprompt},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"http://sti6nanlq.hn-bkt.clouddn.com/exp2/{cm}/{image_filename}"
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
