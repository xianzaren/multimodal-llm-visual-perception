# 彩色编码标量场图形感知中的 MLLM 评估与适配

[English](README.md) | **简体中文**

2025 年项目论文的代码与研究材料：

> **Evaluating and Adapting Multimodal LLMs for Graphical Perception in Color-Encoded Scalar Field Visualization**

[OSF 数据集、提示词与结果](https://osf.io/y4pgm/) | [补充材料](LLMPerception_Supp.pdf)

> **内容范围。** 本仓库介绍 2025 年项目；后续论文仅在最后的[2026 年版本对照](#2026-年后续论文与版本对照)中简要说明。

## 项目概述

彩色编码标量场广泛用于科学和地理空间分析。准确读取这类图像既要理解颜色图例，也要把颜色映射关联回空间区域。2025 年项目将人类参与者实验和 workshop 与 MLLM 评估结合起来，研究模型在无法直接读取底层标量值时完成这一过程的能力。

研究包含两个图形感知任务：

1. **数量估计**：定位颜色与目标标量值对应的坐标。
2. **梯度比较**：判断两个标记区域中哪一个具有更陡的标量梯度。

项目比较 baseline、分解 Step 1/Step 2 提示、思维链（CoT）提示和任务特定微调。

## 2025 年项目范围

### 人类感知流程研究

项目招募了 18 名大学参与者开展组内实验。参与者完成色觉筛查和训练后，分别执行 20 次数量估计和 20 次梯度比较，并回顾自己的分步思考过程。随后进行 27 分钟的 workshop，将参与者分为 5 组完成回顾、头脑风暴和总结。论文报告共收集 640 份参与者回答和 5 组 workshop 总结。

研究从中归纳出两个反复出现的感知步骤：

1. **理解图例**：识别色图、数值范围及目标值或极值对应的颜色。
2. **关联图例与可视化**：定位匹配值，或比较标记区域中的颜色变化速率。

### MLLM 评估与模型适配

2025 年项目评估 GPT-4o、Gemini 1.5 Pro、GLM-4V-9B、InternVL2-8B 和 InternVL2-40B。基准使用 5 种 Perlin 噪声空间频率和 9 种色图，生成 45 张 Task 1 图像和 180 张 Task 2 图像，尺寸为 987 × 630 像素。每张可视化在独立对话中测试 10 次。

项目还使用图像、提示词和真实答案对 InternVL2-8B 进行微调。2025 年论文报告 Task 1 使用 44,775 个训练对，Task 2 使用 9,000 个。分析内容包括：MLLM 在两步感知流程中的失误位置、baseline 与 CoT 对不同任务和模型的影响、微调是否改善任务表现，以及提示策略如何改变模型注意区域。

## 2025 年实验活动索引

下表将 2025 年项目活动与 GitHub 文件、OSF 材料和论文位置对应起来。OSF 文件名区分大小写，表中保留其原始名称。

| 实验活动 | 2025 年范围 | GitHub 记录 | OSF 证据 | 2025 年论文位置 |
| --- | --- | --- | --- | --- |
| 人类参与者实验与 workshop | 18 名参与者；每人 40 次任务；640 份回答；5 个 workshop 小组 | [`file/questionnaire app/`](file/questionnaire%20app/) 和 [`questionnaire or workshop/`](questionnaire%20or%20workshop/) | 仅保留仓库快照 | 第 3 节；表 1 |
| Task 1 基准数据构建 | 数量估计；5 种空间频率 × 9 种色图，共 45 张可视化 | [`CreateTask1Dataset.py`](task1/CreateTask1Dataset.py) 和 [`task1/`](task1/) | [`task1 dataset.zip`](https://osf.io/download/xmnd5/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 5.1.1 节 |
| Task 1 提示策略评估 | Baseline、CoT、分解 Step 1 和分解 Step 2；原始模型流程 | [`codes/api/`](codes/api/)、[`CalculateError.py`](task1/CalculateError.py) 和 [`visualization/`](visualization/) | [`task1.txt`](https://osf.io/download/wtxra/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 4.1–4.3、5.2 节；图 4–5 |
| Task 1 微调 | InternVL2-8B；面向 baseline、CoT 和 linking step 的数据 | [`finetune data/`](finetune%20data/) | [`fine-tune task1 dataset.zip`](https://osf.io/download/be9t6/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0) 中的微调结果工作簿 | 第 4.4、5.2 节；图 3、5 |
| Task 2 基准数据构建 | 梯度比较；180 张可视化 | [`CreateTask2Dataset.py`](task2/CreateTask2Dataset.py) 和 [`task2/`](task2/) | [`task2 dataset.zip`](https://osf.io/download/ysqud/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 5.1.1 节 |
| Task 2 提示策略评估 | Baseline、CoT、分解 Step 1 和分解 Step 2；原始模型流程 | [`codes/api/`](codes/api/)、[`CalculateAccuarcy.py`](task2/CalculateAccuarcy.py) 和 [`visualization/`](visualization/) | [`task2.txt`](https://osf.io/download/fm24q/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 4.1–4.3、5.2 节；图 5 |
| Task 2 微调 | InternVL2-8B；论文报告三类提示共 9,000 个训练对 | [`finetune data/`](finetune%20data/) 和 [`finetune_exp2.jsonl`](finetune_exp2.jsonl) | [`fine-tune task2 dataset.zip`](https://osf.io/download/cbgws/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0) 中的微调结果工作簿 | 第 4.4、5.2 节；图 3、5 |
| 结果汇总与论文图表 | 对数误差/错误率汇总、置信区间、折线图和注意力图 | [`visualization/`](visualization/) 和 [`drawpic/`](drawpic/) | 上述小写 Task 1、Task 2 结果压缩包 | 第 5.2–5.3 节；图 4–6 |

## 仓库内容

```text
.
|-- task1/                         # Task 1 生成、转换、误差和绘图脚本
|-- task2/                         # Task 2 生成、准确率和绘图脚本
|-- codes/api/                     # 原始模型 API 实验脚本
|-- visualization/                # 整理后的可视化脚本和小型结果数据
|-- drawpic/                       # 原始论文绘图脚本
|-- finetune data/                 # 微调数据构建脚本
|-- file/questionnaire app/       # 原始 Flask 问卷源码和模板
|-- questionnaire or workshop/    # 早期人类研究导出
|-- GroupingImages.py              # 图像分组工具
|-- Step1GetRGB.py                 # 色图到 RGB 的提取工具
|-- finetune_exp2.jsonl            # Task 2 微调清单/样例
`-- LLMPerception_Supp.pdf         # 补充材料
```

## 使用项目材料

数据集、提示词、模型输出和实验结果见 [OSF 项目 y4pgm](https://osf.io/y4pgm/)。

安装分析依赖：

```bash
python -m pip install -r requirements.txt
```

运行脚本前，请将输入和输出路径调整为下载文件所在的位置。API 实验脚本需要在本地 `api_info.txt` 中配置相应凭据。

## 2026 年后续论文与版本对照

> **贡献范围说明。** 本仓库维护者在此展示的主要工作是 2025 年项目。本节仅用于记录研究在后续论文中的发展，不应被理解为维护者深度参与了 2026 年修订中的全部新增内容。

[2026 年修订论文](https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf) **MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought** 保留了 2025 年项目的两个任务、两步感知框架、5 种空间频率、9 种色图和 InternVL2-8B 微调，并作出以下更新：

| 对比方面 | 2025 年项目论文 | 2026 年修订论文 |
| --- | --- | --- |
| 研究重点 | 评估 MLLM 图形感知，并考察结构化提示和微调 | 解释 CoT 的模型依赖性反转，并提出应根据模型能力选择提示策略 |
| 人类证据 | 新开展 18 人参与者实验和 workshop | 将已有两步感知流程作为方法框架，并按修订协议从 Reda 等人的数据推导人类基线 |
| 评估模型 | GPT-4o、Gemini 1.5 Pro、GLM-4V-9B、InternVL2-8B、InternVL2-40B | GPT-5.4、Claude Opus 4.7、Gemini 3.1 Pro、Seed 2.0 Pro、InternVL2-8B |
| Task 1 名称 | quantity estimation（数值估计） | value identification（数值识别） |
| 基准图像 | Task 1 为 45 张、Task 2 为 180 张，分辨率 987 × 630 | 数量保持不变，分辨率为 820 × 630 |
| Task 1 微调数据 | 报告 44,775 个图像—提示词对 | 使用 9,450 个训练对：每个标量场提出 21 个数值问题，并加入 30% 随机裁剪增强 |
| 微调方法 | 对 baseline、CoT 和 linking step 使用真实答案监督 | 明确使用 InternVL2-8B LoRA；Task 1 使用交叉熵与空间距离联合损失，Task 2 使用交叉熵 |
| Task 1 指标 | 以 2 为底的对数误差 | 归一化绝对百分比误差；Step 1 的 RGB 输出通过 CIELAB2000 映射回色图数值 |
| 核心结果 | 分析提示和微调在不同任务及模型上的效果 | CoT 对部分模型有益，却让较强模型的 Task 1 相对误差最多增加 84.76%；微调最多降低 43.80% 的相对误差 |

[`codes/api/`](codes/api/) 中的脚本调用 GPT-4o，对应 2025 年工作流。2026 年新增模型输出见 OSF 的 [`Task1.zip`](https://osf.io/download/69f49481b19cd9a17a875458/?view_only=be060a5816bf4edbaaf66a695d57dee0) 和 [`Task2.zip`](https://osf.io/download/69f494bd558fb0c42bd94811/?view_only=be060a5816bf4edbaaf66a695d57dee0)。
