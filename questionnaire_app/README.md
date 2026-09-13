# Questionnaire demo

This directory contains a small, sanitized reconstruction of the local Flask questionnaire in `Final project/file/questionnaire app`. It preserves the core human-study workflow: an anonymous participant code, sequential scalar-field trials, five ordered point selections, automatic lookup of the underlying values, and CSV result recording.

The public version intentionally excludes:

- participant names, demographics, timestamps, and previous response exports;
- the original multi-megabyte scalar-field CSV files and generated image sets;
- the local Excel results workbook;
- color-vision screening plates whose redistribution terms were not documented;
- IDE files, caches, credentials, and hard-coded local paths.

Instead, five deterministic synthetic fields are generated in memory. They demonstrate how the collection system works, but they are **not** the stimuli used to report the paper's results. Download the research datasets and prompts from the [OSF project](https://osf.io/y4pgm/) for research reproduction.

## Run locally

From the repository root:

```bash
python -m pip install -r requirements.txt
python questionnaire_app/app.py
```

Open <http://127.0.0.1:5000>. For a persistent session secret, set `QUESTIONNAIRE_SECRET_KEY` before starting the server. Responses are written to `questionnaire_app/instance/responses.csv`, which is ignored by Git.

## Test

```bash
python -m pytest questionnaire_app/tests
```

This is a research/demo server, not a production data-collection deployment. A real deployment should add an approved consent flow, institutional ethics language, HTTPS, CSRF protection, authenticated administration, a transactional database, backup/retention controls, and a documented anonymization policy.
