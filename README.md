# Evaluating and Adapting MLLMs for Graphical Perception in Color-Encoded Scalar Fields

**English** | [简体中文](README_CN.md)

Code and research materials for the 2025 project manuscript:

> **Evaluating and Adapting Multimodal LLMs for Graphical Perception in Color-Encoded Scalar Field Visualization**

[OSF datasets, prompts, and results](https://osf.io/y4pgm/) | [Supplementary material](LLMPerception_Supp.pdf)

> **Scope.** This repository documents the 2025 project. A later paper is summarized only in the final [2026 comparison](#2026-follow-up-paper-and-comparison).

## Overview

Color-encoded scalar fields are widely used in scientific and geospatial analysis, but reading them requires both understanding the color legend and linking that mapping back to spatial regions. The 2025 project combined a human empirical study and workshop with an evaluation of how multimodal large language models (MLLMs) perform this workflow without direct access to the underlying scalar values.

We study two graphical-perception tasks:

1. **Quantity estimation** — locate a coordinate whose color corresponds to a target scalar value.
2. **Gradient comparison** — determine which of two marked regions has the steeper scalar gradient.

The project compares baseline prompting, decomposed Step 1/Step 2 prompting, chain-of-thought (CoT) prompting, and task-specific fine-tuning.

## 2025 project scope

### Human perception workflow study

The project recruited 18 university participants for a within-subjects study. After color-vision screening and training, each participant completed 20 quantity-estimation trials and 20 gradient-comparison trials, then reflected on their step-by-step reasoning. A 27-minute workshop organized the participants into five groups for recall, brainstorming, and summarization. The manuscript reports 640 empirical-study responses and five group-level workshop summaries.

This work identified two recurring perception steps:

1. **Legend understanding** — infer the colormap, value range, and colors representing relevant values or extrema.
2. **Linking legend to visualization** — locate the matching value or compare color-change rates in marked regions.

### MLLM evaluation and model adaptation

The 2025 project evaluates GPT-4o, Gemini 1.5 Pro, GLM-4V-9B, InternVL2-8B, and InternVL2-40B. The benchmark uses five Perlin-noise spatial frequencies and nine colormaps, producing 45 Task 1 visualizations and 180 Task 2 visualizations at 987 × 630 pixels. Each visualization was tested 10 times in separate dialog sessions.

The project also fine-tunes InternVL2-8B on image-prompt-ground-truth pairs. The 2025 manuscript reports 44,775 Task 1 pairs and 9,000 Task 2 pairs. Its analysis investigates where MLLMs fail in the two-step workflow, how baseline and CoT prompts affect different tasks and models, whether fine-tuning improves task performance, and how prompting changes model attention.

## 2025 experiment activity index

This index connects the 2025 project activities to the corresponding GitHub files, OSF artifacts, and manuscript sections. OSF filenames are case-sensitive and are reproduced exactly.

| Experimental activity | 2025 scope | GitHub record | OSF evidence | 2025 manuscript |
| --- | --- | --- | --- | --- |
| Human study and workshop | 18 participants; 40 trials per participant; 640 responses; five workshop groups | [`file/questionnaire app/`](file/questionnaire%20app/) and [`questionnaire or workshop/`](questionnaire%20or%20workshop/) | Repository snapshot only | Sec. 3; Table 1 |
| Task 1 benchmark construction | Quantity estimation; 5 spatial frequencies × 9 colormaps = 45 visualizations | [`CreateTask1Dataset.py`](task1/CreateTask1Dataset.py) and [`task1/`](task1/) | [`task1 dataset.zip`](https://osf.io/download/xmnd5/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Sec. 5.1.1 |
| Task 1 prompting evaluation | Baseline, CoT, decomposed Step 1, and decomposed Step 2; original model workflow | [`codes/api/`](codes/api/), [`CalculateError.py`](task1/CalculateError.py), and [`visualization/`](visualization/) | [`task1.txt`](https://osf.io/download/wtxra/?view_only=be060a5816bf4edbaaf66a695d57dee0); [`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Secs. 4.1–4.3 and 5.2; Figs. 4–5 |
| Task 1 fine-tuning | InternVL2-8B; baseline-, CoT-, and linking-step-oriented data | [`finetune data/`](finetune%20data/) | [`fine-tune task1 dataset.zip`](https://osf.io/download/be9t6/?view_only=be060a5816bf4edbaaf66a695d57dee0); fine-tuned workbooks in [`task1.zip`](https://osf.io/download/a8mnq/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Sec. 4.4 and Sec. 5.2; Figs. 3 and 5 |
| Task 2 benchmark construction | Gradient comparison; 180 visualizations | [`CreateTask2Dataset.py`](task2/CreateTask2Dataset.py) and [`task2/`](task2/) | [`task2 dataset.zip`](https://osf.io/download/ysqud/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Sec. 5.1.1 |
| Task 2 prompting evaluation | Baseline, CoT, decomposed Step 1, and decomposed Step 2; original model workflow | [`codes/api/`](codes/api/), [`CalculateAccuarcy.py`](task2/CalculateAccuarcy.py), and [`visualization/`](visualization/) | [`task2.txt`](https://osf.io/download/fm24q/?view_only=be060a5816bf4edbaaf66a695d57dee0); [`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Secs. 4.1–4.3 and 5.2; Fig. 5 |
| Task 2 fine-tuning | InternVL2-8B; 9,000 reported pairs across the three prompt types | [`finetune data/`](finetune%20data/) and [`finetune_exp2.jsonl`](finetune_exp2.jsonl) | [`fine-tune task2 dataset.zip`](https://osf.io/download/cbgws/?view_only=be060a5816bf4edbaaf66a695d57dee0); fine-tuned workbooks in [`task2.zip`](https://osf.io/download/62n7t/?view_only=be060a5816bf4edbaaf66a695d57dee0) | Sec. 4.4 and Sec. 5.2; Figs. 3 and 5 |
| Result aggregation and figures | Log-error/error-rate summaries, confidence intervals, line charts, and attention maps | [`visualization/`](visualization/) and [`drawpic/`](drawpic/) | The lowercase Task 1 and Task 2 result archives linked above | Secs. 5.2–5.3; Figs. 4–6 |

## Repository contents

```text
.
|-- task1/                         # Task 1 generation, conversion, error, and plotting scripts
|-- task2/                         # Task 2 generation, accuracy, and plotting scripts
|-- codes/api/                     # Original model API experiment scripts
|-- visualization/                # Curated visualization scripts and compact result data
|-- drawpic/                       # Original paper-figure scripts
|-- finetune data/                 # Fine-tuning data-construction scripts
|-- file/questionnaire app/       # Original Flask questionnaire source and templates
|-- questionnaire or workshop/    # Legacy human-study exports
|-- GroupingImages.py              # Image grouping utility
|-- Step1GetRGB.py                 # Colormap-to-RGB extraction utility
|-- finetune_exp2.jsonl            # Task 2 fine-tuning manifest/sample
`-- LLMPerception_Supp.pdf         # Supplementary material
```

## Using the materials

Datasets, prompts, model outputs, and experiment results are available from [OSF project y4pgm](https://osf.io/y4pgm/).

Install the analysis dependencies with:

```bash
python -m pip install -r requirements.txt
```

Before running a script, update its input and output paths to the downloaded files. The API experiment scripts require a local `api_info.txt` containing the relevant credentials.

## 2026 follow-up paper and comparison

> **Contribution scope.** The maintainer's primary contribution represented by this repository is the 2025 project. This section records how the research was extended in a later paper and should not be interpreted as a claim of deep participation in every addition made for the 2026 revision.

The [2026 revised manuscript](https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf), **MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought**, retains the two tasks, two-step perception framework, five spatial frequencies, nine colormaps, and InternVL2-8B fine-tuning from the 2025 project. It then updates the study as follows:

| Aspect | 2025 project manuscript | 2026 revised manuscript |
| --- | --- | --- |
| Research emphasis | Evaluating MLLM graphical perception and testing structured prompting and fine-tuning | Explaining the model-dependent inversion of CoT and motivating capability-aware prompting |
| Human evidence | New empirical study and workshop with 18 participants | Uses the established two-step workflow as scaffolding and derives human baselines from Reda et al. under the revised evaluation protocol |
| Evaluated models | GPT-4o, Gemini 1.5 Pro, GLM-4V-9B, InternVL2-8B, InternVL2-40B | GPT-5.4, Claude Opus 4.7, Gemini 3.1 Pro, Seed 2.0 Pro, InternVL2-8B |
| Task terminology | Task 1 is called quantity estimation | Task 1 is called value identification |
| Benchmark rendering | 45 Task 1 and 180 Task 2 visualizations at 987 × 630 pixels | The same counts at 820 × 630 pixels |
| Task 1 fine-tuning | Reports 44,775 image-prompt pairs | Uses 9,450 pairs from 21 value queries per field plus 30% random-crop augmentation |
| Fine-tuning method | Ground-truth supervision for baseline, CoT, and linking-step prompts | Specifies LoRA for InternVL2-8B, CE plus a spatial-distance term for Task 1, and CE for Task 2 |
| Task 1 metric | Base-2 logarithmic error | Normalized absolute percentage error; Step 1 RGB outputs are mapped back through the colormap with CIELAB2000 |
| Principal result | Prompting and fine-tuning effects are examined across tasks and models | CoT helps some models but harms stronger models by up to 84.76% relative error on Task 1; fine-tuning improves error by up to 43.80% |

The GitHub API scripts in [`codes/api/`](codes/api/) use GPT-4o and correspond to the 2025 workflow. Additional 2026 model outputs are available in the OSF [`Task1.zip`](https://osf.io/download/69f49481b19cd9a17a875458/?view_only=be060a5816bf4edbaaf66a695d57dee0) and [`Task2.zip`](https://osf.io/download/69f494bd558fb0c42bd94811/?view_only=be060a5816bf4edbaaf66a695d57dee0) packages.
