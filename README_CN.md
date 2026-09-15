# 彩色编码标量场中的 MLLM 感知

[English](README.md) | **简体中文**

以下论文的官方代码与研究材料：

> **MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought**  
> Minyi Liu、Yue Zhao、Xiaoyang Song、Shufan Qian、Yulong Bian、Qiong Zeng（2026）

[当前论文](https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf) | [OSF 数据集、提示词与结果](https://osf.io/y4pgm/) | [补充材料](LLMPerception_Supp.pdf)

## 项目概述

彩色编码标量场广泛用于科学和地理空间分析。准确读取这类图像既要理解颜色图例，也要把颜色映射关联回空间区域。本项目评估多模态大语言模型（MLLM）在无法直接读取底层标量值时完成这一过程的能力。

研究包含两个图形感知任务：

1. **数值识别**：定位颜色与目标标量值对应的坐标。
2. **梯度比较**：判断两个标记区域中哪一个具有更陡的标量梯度。

实验比较 baseline、分步提示、思维链（CoT）提示和任务特定微调。

## 主要发现

- **空间定位是主要瓶颈。** 对各模型而言，理解图例明显比把图例值关联到标量场位置更容易。
- **CoT 的作用取决于模型，而非普遍有益。** 显式分步指导会改善部分模型和任务，但也可能降低更强模型的表现；Task 1 报告的最大相对下降为 84.76%。
- **微调效果更加稳定。** 任务特定适配可同时改善 InternVL2-8B 的两个任务，最高相对误差下降为 43.80%。
- **提示设计应与模型能力匹配。** 对一个 MLLM 有帮助的提示，可能让另一个模型过度思考或关注无效视觉证据。

## 实验设计

结构化提示遵循两阶段感知流程：

1. **理解图例**：识别色图、数值范围及目标值或极值对应的颜色。
2. **关联图例与可视化**：定位匹配值，或比较标记区域中的颜色变化速率。

2026 年研究评估 GPT-5.4、Claude Opus 4.7、Gemini 3.1 Pro、Seed 2.0 Pro 和 InternVL2-8B。基准使用 5 种 Perlin 噪声空间频率和 9 种色图，生成 45 张 Task 1 图像和 180 张 Task 2 图像，尺寸均为 820 × 630 像素。

Task 1 微调使用 9,450 个图像—提示词对，Task 2 使用 9,000 个。大型数据集和完整实验输出存放在 OSF，不在 Git 中重复保存。

## 实验活动索引

下表将论文中报告的实验活动与相应代码、提示词、数据集、结果压缩包及论文章节对应起来。OSF 文件名区分大小写；由于本仓库不能调整已经归档的 OSF 文件，表中保留其原始名称。

| 实验活动 | 配置与规模 | GitHub 记录 | OSF 证据 | 论文位置 |
| --- | --- | --- | --- | --- |
| Task 1 基准数据构建 | 数值识别；5 种空间频率 × 9 种色图，共 45 张可视化 | [`CreateTask1Dataset.py`](task1/CreateTask1Dataset.py) 和 [`task1/`](task1/) | [`task1 dataset.zip`](https://osf.io/download/xmnd5/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 4.1 节；图 2 |
| Task 1 提示策略评估 | 在所评估 MLLM 上运行 Baseline、CoT、分解 Step 1 和分解 Step 2 | [`codes/api/`](codes/api/)、[`CalculateError.py`](task1/CalculateError.py) 和 [`visualization/`](visualization/) | [`task1.txt`](https://osf.io/download/wtxra/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`Task1.zip`](https://osf.io/download/69f49481b19cd9a17a875458/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 3.2、4.2 节；图 2 |
| Task 1 微调 | InternVL2-8B；9,450 个图像—提示词对；包含面向 Baseline、CoT 和 Step 2 的数据构建 | [`finetune data/`](finetune%20data/) | [`fine-tune task1 dataset.zip`](https://osf.io/download/be9t6/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0) 中的微调结果工作簿 | 第 3.3、4.2 节；图 2 |
| Task 2 基准数据构建 | 梯度比较；180 张可视化，每张在论文评估中查询 10 次 | [`CreateTask2Dataset.py`](task2/CreateTask2Dataset.py) 和 [`task2/`](task2/) | [`task2 dataset.zip`](https://osf.io/download/ysqud/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 4.1 节；图 3–4 |
| Task 2 提示策略评估 | 在所评估 MLLM 上运行 Baseline、CoT、分解 Step 1 和分解 Step 2 | [`codes/api/`](codes/api/)、[`CalculateAccuarcy.py`](task2/CalculateAccuarcy.py) 和 [`visualization/`](visualization/) | [`task2.txt`](https://osf.io/download/fm24q/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`Task2.zip`](https://osf.io/download/69f494bd558fb0c42bd94811/?view_only=be060a5816bf4edbaaf66a695d57dee0) | 第 3.2、4.3 节；图 3–4 |
| Task 2 微调 | InternVL2-8B；9,000 个图像—提示词对；包含面向 Baseline、CoT 和 Step 2 的数据构建 | [`finetune data/`](finetune%20data/) 和 [`finetune_exp2.jsonl`](finetune_exp2.jsonl) | [`fine-tune task2 dataset.zip`](https://osf.io/download/cbgws/?view_only=be060a5816bf4edbaaf66a695d57dee0)；[`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0) 中的微调结果工作簿 | 第 3.3、4.3 节；图 3 |
| 人类工作流探索性收集 | 早期提示设计阶段使用的问卷与 workshop 材料 | [`file/questionnaire app/`](file/questionnaire%20app/) 和 [`questionnaire or workshop/`](questionnaire%20or%20workshop/) | 仅保留仓库快照 | 历史设计证据；并非 2026 论文中人类基线的数据来源 |
| 结果汇总与论文图表 | 误差/准确率汇总、置信区间、折线图及注意力/选择可视化 | [`visualization/`](visualization/) 和 [`drawpic/`](drawpic/) | 上述 Task 1、Task 2 结果压缩包 | 图 2–4 及补充材料 |

**OSF 结果包说明。** 小写的 `task1.zip`、`task2.zip` 包含汇总工作簿、微调结果以及沿用 `8b`、`40b` 等早期模型标签的文件；大写的 `Task1.zip`、`Task2.zip` 包含更多新模型输出，包括 GPT-5.4、Claude Opus 4.7、Gemini 3.1 Pro 和 Seed/Doubao 记录。上述名称均按 OSF 现有归档保留，请使用本表判断其用途。

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
|-- docs/                          # 本地材料审计说明
|-- GroupingImages.py              # 图像分组工具
|-- Step1GetRGB.py                 # 色图到 RGB 的提取工具
|-- finetune_exp2.jsonl            # Task 2 微调清单/样例
`-- LLMPerception_Supp.pdf         # 补充材料
```

该仓库同时包含整理后的公开材料和已有本地研究源码快照。部分脚本保留了原实验阶段使用的目录、文件名和模型设置。`codes/api/` 主要对应早期 API 工作流；OSF 项目保存了用于研究审阅的数据集、提示词和实验结果。

问卷和 workshop 文件记录了促成两阶段感知流程的早期工作，但不是 2026 论文中人类基线的来源。再次使用或分发参与者导出前，应检查知情同意和可识别字段。

## 数据与可复现性

OSF 项目包含：

- 两个任务的基准数据集；
- 微调数据集；
- baseline、分步和 CoT 提示词；
- 模型输出和实验结果。

请从 [OSF 项目 y4pgm](https://osf.io/y4pgm/) 下载。微调归档达到数 GB，应继续保留在 OSF，而不是重复提交到 GitHub。

安装分析依赖：

```bash
python -m pip install -r requirements.txt
```

本仓库是研究快照，不是单命令复现包。运行脚本前请检查输入/输出路径，并将其指向相应 OSF 文件。原始 API 脚本还需要本地 `api_info.txt`；该凭据文件已被 Git 明确排除。

## 隐私与负责任使用

不要提交参与者姓名、联系方式、人口统计字段、提交时间、API 凭据、模型权重、私人论文或完整本地实验目录。早期人类研究导出可能包含可识别字段，只能在符合知情同意和机构研究伦理要求的情况下使用。

## 引用

如果本项目对你的研究有帮助，请引用 2026 年论文：

```bibtex
@misc{liu2026mllmperception,
  title  = {MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought},
  author = {Liu, Minyi and Zhao, Yue and Song, Xiaoyang and Qian, Shufan and Bian, Yulong and Zeng, Qiong},
  year   = {2026},
  url    = {https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf}
}
```

## 许可证

项目尚未声明开源许可证。在添加许可证前，仓库虽然可以公开查看，但不会自动授予复用权。若要在关联研究材料规定范围之外重新分发代码或数据，请先联系作者。
