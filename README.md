# MLLM Perception of Color-Encoded Scalar Fields

**English** | [简体中文](README_CN.md)

Official code and research materials for:

> **MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought**  
> Minyi Liu, Yue Zhao, Xiaoyang Song, Shufan Qian, Yulong Bian, and Qiong Zeng (2026)

[Current manuscript](https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf) | [OSF datasets, prompts, and results](https://osf.io/y4pgm/) | [Supplementary material](LLMPerception_Supp.pdf)

## Overview

Color-encoded scalar fields are widely used in scientific and geospatial analysis, but reading them requires both understanding the color legend and linking that mapping back to spatial regions. This project evaluates how multimodal large language models (MLLMs) perform that workflow without direct access to the underlying scalar values.

We study two graphical-perception tasks:

1. **Value identification** — locate a coordinate whose color corresponds to a target scalar value.
2. **Gradient comparison** — determine which of two marked regions has the steeper scalar gradient.

The evaluation compares baseline prompting, decomposed-step prompting, chain-of-thought (CoT) prompting, and task-specific fine-tuning.

## Main findings

- **Spatial localization is the main bottleneck.** Across models, interpreting the legend is substantially easier than linking a legend value to a location in the scalar field.
- **CoT is model-dependent rather than universally beneficial.** Explicit step-by-step guidance improves some models and tasks, but can degrade stronger models; the largest reported relative degradation is 84.76% on Task 1.
- **Fine-tuning is more consistent.** Task-specific adaptation improves InternVL2-8B across both tasks, with relative error reductions of up to 43.80%.
- **Prompting should be capability-aware.** A prompt that helps one MLLM may cause another to overthink or attend to less useful visual evidence.

## Experimental design

The structured prompting framework follows a two-stage perception workflow:

1. **Legend understanding** — infer the colormap, value range, and colors representing relevant values or extrema.
2. **Linking legend to visualization** — locate the matching value or compare color-change rates in marked regions.

The 2026 study evaluates five MLLMs: GPT-5.4, Claude Opus 4.7, Gemini 3.1 Pro, Seed 2.0 Pro, and InternVL2-8B. The benchmark uses five Perlin-noise spatial frequencies and nine colormaps, producing 45 Task 1 visualizations and 180 Task 2 visualizations at 820 × 630 pixels.

Fine-tuning uses 9,450 image-prompt pairs for Task 1 and 9,000 pairs for Task 2. Large datasets and complete experimental outputs are hosted on OSF instead of being duplicated in Git.

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

The repository combines the curated public materials with existing local research-source snapshots. Some scripts retain the directory layout, filenames, and model settings used during their original experiment stage. `codes/api/` mainly reflects the earlier API workflow, while the OSF project contains the archived datasets, prompts, and results used for research review.

The questionnaire and workshop files document an earlier phase that informed the two-stage perception workflow. They are not the source of the human baselines reported in the 2026 manuscript. Existing participant exports should be reviewed for consent and identifying fields before reuse or redistribution.

## Data and reproducibility

The OSF project contains:

- benchmark datasets for both tasks;
- fine-tuning datasets;
- baseline, decomposed-step, and CoT prompts;
- model outputs and experiment results.

Download them from [OSF project y4pgm](https://osf.io/y4pgm/). The fine-tuning archives are several gigabytes, so they should remain on OSF rather than in this repository.

Install the analysis dependencies with:

```bash
python -m pip install -r requirements.txt
```

This repository is a research snapshot rather than a single-command reproduction package. Before running a script, inspect its input/output paths and point them to the corresponding OSF files. Original API scripts also require a local `api_info.txt`; that credential file is deliberately excluded from Git.

## Privacy and responsible use

Do not commit participant names, contact details, demographics, submission timestamps, API credentials, model weights, private manuscripts, or raw local experiment folders. Legacy human-study exports may contain identifying fields and should be reused only under the applicable consent and research-ethics requirements.

## Citation

If this work supports your research, cite the 2026 manuscript:

```bibtex
@misc{liu2026mllmperception,
  title  = {MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought},
  author = {Liu, Minyi and Zhao, Yue and Song, Xiaoyang and Qian, Shufan and Bian, Yulong and Zeng, Qiong},
  year   = {2026},
  url    = {https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf}
}
```

## License

No open-source license has been declared yet. Until a license is added, the repository is publicly viewable but reuse rights are not granted automatically. Please contact the authors before redistributing code or data outside the terms stated by the linked research artifacts.
