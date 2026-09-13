# MLLM Perception of Color-Encoded Scalar Fields

Official code and research materials for:

> **MLLM Perception of Color-Encoded Scalar Fields Reveals Model-Dependent Inversion of Chain-of-Thought**  
> Minyi Liu, Yue Zhao, Xiaoyang Song, Shufan Qian, Yulong Bian, and Qiong Zeng (2026)

[Current manuscript](https://jackz.cn/static/media/paper/03e096af81174c169c62568de5562038.pdf) | [OSF datasets, prompts, and results](https://osf.io/y4pgm/) | [Supplementary material](LLMPerception_Supp.pdf)

## Overview

Color-encoded scalar fields are widely used in scientific and geospatial analysis, but reading them requires both understanding the color legend and linking that mapping back to spatial regions. This project evaluates how multimodal large language models (MLLMs) perform that workflow without direct access to the underlying scalar values.

We study two graphical-perception tasks:

1. **Value identification** - locate a coordinate whose color corresponds to a target scalar value.
2. **Gradient comparison** - determine which of two marked regions has the steeper scalar gradient.

The evaluation compares baseline prompting, decomposed-step prompting, chain-of-thought (CoT) prompting, and task-specific fine-tuning.

## Main findings

- **Spatial localization is the main bottleneck.** Across models, interpreting the legend is substantially easier than linking a legend value to a location in the scalar field.
- **CoT is model-dependent rather than universally beneficial.** Explicit step-by-step guidance improves some models and tasks, but can degrade stronger models; the largest reported relative degradation is 84.76% on Task 1.
- **Fine-tuning is more consistent.** Task-specific adaptation improves InternVL2-8B across both tasks, with relative error reductions of up to 43.80%.
- **Prompting should be capability-aware.** A prompt that helps one MLLM may cause another to overthink or attend to less useful visual evidence.

## Experimental design

The structured prompting framework follows a two-stage perception workflow:

1. **Legend understanding** - infer the colormap, value range, and colors representing relevant values or extrema.
2. **Linking legend to visualization** - locate the matching value or compare color-change rates in marked regions.

The 2026 study evaluates five MLLMs: GPT-5.4, Claude Opus 4.7, Gemini 3.1 Pro, Seed 2.0 Pro, and InternVL2-8B. The benchmark uses five Perlin-noise spatial frequencies and nine colormaps, producing 45 Task 1 visualizations and 180 Task 2 visualizations at 820 x 630 pixels.

Fine-tuning uses 9,450 image-prompt pairs for Task 1 and 9,000 pairs for Task 2. Large datasets and complete experimental outputs are hosted on OSF instead of being duplicated in Git.

## Repository contents

```text
.
|-- task1/                         # Value-identification dataset and evaluation scripts
|-- task2/                         # Gradient-comparison dataset and evaluation scripts
|-- visualization/                # Figure and result-visualization scripts
|-- questionnaire_app/             # Lightweight, privacy-safe questionnaire demo
|-- questionnaire or workshop/    # Legacy human-study materials (not modified here)
|-- GroupingImages.py              # Image grouping utility
|-- Step1GetRGB.py                 # Colormap-to-RGB extraction utility
|-- finetune_exp2.jsonl            # Task 2 fine-tuning manifest/sample
`-- LLMPerception_Supp.pdf         # Supplementary material
```

The human questionnaire and workshop files document an earlier phase of the project that informed the two-stage perception workflow. They are not the source of the human baselines reported in the 2026 manuscript. These pre-existing participant exports are not modified by this update and should be reviewed for consent and identifying fields before reuse or redistribution.

A cleaned, code-only demo of the questionnaire workflow is available in [`questionnaire_app/`](questionnaire_app/). It generates small synthetic stimuli at runtime and does not contain participant records or the original experiment assets.

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

The scripts are a research snapshot and some expect the directory layout used during the experiments. Before running a script, update its input and output paths to point to the corresponding files downloaded from OSF.

## Privacy and responsible use

Do not commit participant names, contact details, demographics, submission timestamps, API credentials, model weights, private manuscripts, or raw local experiment folders. The legacy human-study exports predate this documentation update and may contain identifying fields; review and anonymize them only with appropriate authorization. If you reuse any human-study materials, follow the consent terms and research-ethics requirements applicable to your institution.

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
