# Local Materials Audit

This document records the publication review of the working directory used during the project. It is intended to prevent accidental uploads of private, duplicated, or very large artifacts.

## Summary

The local project archive contains approximately 87,000 files and 21.3 GB of data. Most of that material should not be copied directly into GitHub. Large research datasets and experiment outputs are already better served by the linked OSF project.

## Suitable for GitHub after review

- Maintained Python source files for dataset generation, evaluation, and visualization.
- Prompt templates with API credentials removed.
- The questionnaire application's source code after separating participant results and large stimulus data.
- Small representative images required to explain the tasks.
- Documentation describing environment setup, expected directory layout, and reproduction commands.
- Aggregated or fully anonymized result tables when their release is consistent with participant consent.

## Keep on OSF or external artifact storage

- Multi-gigabyte fine-tuning datasets.
- Full benchmark image collections and raw scalar-field matrices.
- Complete model outputs and large experiment-result archives.
- Fine-tuned model checkpoints.

## Do not publish

- API keys, tokens, local credential files, and machine-specific configuration.
- Participant names, timestamps, contact information, or linkable demographics.
- Raw questionnaire exports unless they have been anonymized and release is covered by consent.
- IDE caches, Python environments, `__pycache__`, test caches, and temporary Office files.
- Third-party papers, pretrained weights, or copied upstream repositories unless their licenses explicitly permit redistribution and attribution is preserved.
- Draft theses, meeting notes, personal presentations, and unrelated coursework.

## Questionnaire application

The local Flask questionnaire is useful research software, but its current folder mixes source code with five large CSV scalar fields and a live `result.xlsx` export. Before publication, the application should be packaged separately, configured through environment variables, supplied with synthetic sample data, and documented with an explicit privacy notice. The live result workbook must never be committed.
