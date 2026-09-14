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
