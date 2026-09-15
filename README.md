# Evaluating and Adapting MLLMs for Graphical Perception in Color-Encoded Scalar Fields

**English** | [简体中文](README_CN.md)

Research code and project materials for the 2025 project manuscript:

> **Evaluating and Adapting Multimodal LLMs for Graphical Perception in Color-Encoded Scalar Field Visualization**
> 2025 project manuscript (anonymous submission copy)

[OSF datasets, prompts, and results](https://osf.io/y4pgm/) | [Supplementary material](LLMPerception_Supp.pdf)

> **Version scope.** This repository mainly preserves the implementation and research materials completed during the 2025 project stage. A later 2026 manuscript is documented only in the final [follow-up comparison](#2026-follow-up-paper-and-comparison).

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
|-- docs/                          # Local-material audit notes
|-- GroupingImages.py              # Image grouping utility
|-- Step1GetRGB.py                 # Colormap-to-RGB extraction utility
|-- finetune_exp2.jsonl            # Task 2 fine-tuning manifest/sample
`-- LLMPerception_Supp.pdf         # Supplementary material
```

The repository combines curated public materials with the 2025 research-source snapshot. Some scripts retain the directory layout, filenames, and model settings used during that project stage. `codes/api/` reflects the original GPT-4o API workflow, while the OSF project combines archived materials from the 2025 project and the 2026 revision.

The questionnaire and workshop files document the 2025 empirical-study phase that informed the two-stage perception workflow. They are not the source of the human baselines reported in the 2026 manuscript. Existing participant exports should be reviewed for consent and identifying fields before reuse or redistribution.

## Data and reproducibility

The OSF project contains materials from both research stages:

- benchmark datasets for both tasks;
- fine-tuning datasets;
- baseline, decomposed-step, and CoT prompts;
- lowercase result packages containing aggregate workbooks, fine-tuning results, and earlier-model records;
- uppercase result packages containing additional outputs for the 2026 model panel.

Access the complete archives through [OSF project y4pgm](https://osf.io/y4pgm/).

Install the analysis dependencies with:

```bash
python -m pip install -r requirements.txt
```

This repository is a research snapshot rather than a single-command reproduction package for either manuscript version. Before running a script, identify its version, inspect its input/output paths, and point it to the corresponding OSF files. Original API scripts also require a local `api_info.txt`; that credential file is deliberately excluded from Git.

## Privacy and responsible use

Do not commit participant names, contact details, demographics, submission timestamps, API credentials, model weights, private manuscripts, or raw local experiment folders. Legacy human-study exports may contain identifying fields and should be reused only under the applicable consent and research-ethics requirements.

## Citation

The 2025 manuscript is an anonymous submission copy and is identified here by title and project year. The named 2026 follow-up citation is provided in the final section below.

## License

No open-source license has been declared yet. Until a license is added, the repository is publicly viewable but reuse rights are not granted automatically. Please contact the authors before redistributing code or data outside the terms stated by the linked research artifacts.

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

The GitHub API scripts currently preserved in [`codes/api/`](codes/api/) explicitly use GPT-4o and therefore document the 2025 workflow. The additional 2026 proprietary-model outputs are archived on OSF in the uppercase [`Task1.zip`](https://osf.io/download/69f49481b19cd9a17a875458/?view_only=be060a5816bf4edbaaf66a695d57dee0) and [`Task2.zip`](https://osf.io/download/69f494bd558fb0c42bd94811/?view_only=be060a5816bf4edbaaf66a695d57dee0) packages. The lowercase `task1.zip` and `task2.zip` packages retain aggregate workbooks, fine-tuning results, and earlier labels such as `8b` and `40b`.

If the follow-up paper is cited, use:

```bibtex
@misc{liu2026mllmperception,
  title  = {MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought},
  author = {Liu, Minyi and Zhao, Yue and Song, Xiaoyang and Qian, Shufan and Bian, Yulong and Zeng, Qiong},
  year   = {2026},
  url    = {https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf}
}
```
