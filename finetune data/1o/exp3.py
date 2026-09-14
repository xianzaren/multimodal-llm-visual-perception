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

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):  # 添加行号，帮助调试
                try:
                    #print(f"📄 读取第 {line_num} 行: {line.strip()}")
                    # f1_greyscale_10.png + 真实曲线是第4条
                    match = re.match(r"(\w+)_(\w+)_(\d+)\.png\s\+\s真实曲线是第\s(\d+)\s条", line)
                    if match:
                        fre_name = match.group(1)
                        color_name = match.group(2)
                        num = match.group(3)
                        filename = fre_name + "_" + color_name + "_" + str(num)
                        curve_number = match.group(4)

                        #print(f"🔑 提取的文件名: {filename}, 曲线编号: {curve_number}")
                        results[filename] = curve_number
                    else:
                        print(f"⚠️ 无法匹配该行内容: {line.strip()}")
                except Exception as e:
                    print(f"❌ 处理第 {line_num} 行时出错: {e}")
    except Exception as e:
        print(f"❌ 打开文件时发生错误: {str(e)}")  # 输出完整的异常信息

    return results


base_path = '../../../image_finetune/exp3_2/'
images_path = "../../image_finetune/exp3_2/"

output_file = "finetune_exp3.jsonl"
id_counter = 0

if os.path.exists(output_file):
    os.remove(output_file)

def process_file(cm):
    global id_counter
    cm_path = os.path.join(base_path, cm)  # 文件夹路径
    png_files = [f for f in os.listdir(cm_path) if f.endswith('.png')]  # 文件夹下的所有图片

    res_path = os.path.join(cm_path, "result.txt")
    ans = parse_expected_results(res_path)

    for png_file in png_files:
        with open(output_file, 'a', encoding='utf-8') as f_out:

            image_filename = os.path.splitext(png_file)[0]
            image_path = os.path.join(f"exp3/{cm}", image_filename).replace("\\", "/")
            image_path2 = image_path + ".png"

            conversation = [
                {
                    "from": "human",
                    "value": f"<image>\n Imagine a line from A to B. Select the elevation profile below that most closely matches its slope."
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
                "width": 1754,
                "height": 854
            }
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"记录了{id_counter}条数据")
            id_counter += 1

    # del df
    # gc.collect()

for cm in colormap_list:
    process_file(cm)

print(f"数据集已成功保存为 {output_file}")
