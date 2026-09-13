"""Lightweight questionnaire demo for scalar-field perception experiments."""

from __future__ import annotations

import csv
import io
import json
import os
import re
import secrets
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import matplotlib
import numpy as np
from flask import Flask, abort, redirect, render_template, request, send_file, session, url_for
from PIL import Image


matplotlib.use("Agg")

FIELD_WIDTH = 480
FIELD_HEIGHT = 360
TARGET_VALUES = (1000, 750, 500, 250, 0)
TRIALS = (
    {"seed": 11, "colormap": "gray"},
    {"seed": 23, "colormap": "Blues_r"},
    {"seed": 37, "colormap": "hot"},
    {"seed": 53, "colormap": "coolwarm"},
    {"seed": 71, "colormap": "viridis"},
)
PARTICIPANT_CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
RESULT_COLUMNS = (
    "response_id",
    "submitted_at_utc",
    "participant_code",
    "trial_index",
    "seed",
    "colormap",
    "points_json",
    "observed_values_json",
    "absolute_errors_json",
)


@lru_cache(maxsize=len(TRIALS))
def build_scalar_field(trial_index: int) -> np.ndarray:
    """Build a deterministic, smooth synthetic field scaled to [0, 1000]."""
    if not 0 <= trial_index < len(TRIALS):
        raise IndexError("trial index out of range")

    seed = TRIALS[trial_index]["seed"]
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:1:complex(FIELD_HEIGHT), 0:1:complex(FIELD_WIDTH)]

    field = (
        0.70 * np.sin(2 * np.pi * (2 + seed % 3) * x)
        + 0.55 * np.cos(2 * np.pi * (2 + seed % 4) * y)
        + 0.30 * np.sin(2 * np.pi * (x + y) * (1 + seed % 2))
    )
    for _ in range(5):
        center_x, center_y = rng.uniform(0.1, 0.9, size=2)
        spread = rng.uniform(0.04, 0.16)
        amplitude = rng.uniform(-1.0, 1.0)
        field += amplitude * np.exp(
            -((x - center_x) ** 2 + (y - center_y) ** 2) / (2 * spread**2)
        )

    field -= field.min()
    field /= field.max()
    return np.rint(field * 1000).astype(np.int16)


def colormap_css(colormap_name: str) -> str:
    """Return CSS color stops matching the Matplotlib colormap."""
    cmap = matplotlib.colormaps[colormap_name]
    stops = []
    for position in np.linspace(0, 1, 9):
        red, green, blue, _ = cmap(position)
        stops.append(
            f"rgb({round(red * 255)}, {round(green * 255)}, {round(blue * 255)}) "
            f"{round(position * 100)}%"
        )
    return ", ".join(stops)


def validate_points(raw_points: str) -> list[tuple[int, int]]:
    try:
        decoded = json.loads(raw_points)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("points_json must be valid JSON") from exc

    if not isinstance(decoded, list) or len(decoded) != len(TARGET_VALUES):
        raise ValueError(f"exactly {len(TARGET_VALUES)} points are required")

    points: list[tuple[int, int]] = []
    for point in decoded:
        if not isinstance(point, dict):
            raise ValueError("each point must be an object")
        x, y = point.get("x"), point.get("y")
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("point coordinates must be integers")
        if not 0 <= x < FIELD_WIDTH or not 0 <= y < FIELD_HEIGHT:
            raise ValueError("point coordinates are outside the stimulus")
        points.append((x, y))
    return points


def append_result(path: Path, row: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("QUESTIONNAIRE_SECRET_KEY") or secrets.token_hex(32),
        RESULTS_PATH=str(Path(app.instance_path) / "responses.csv"),
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @app.get("/")
    def intro():
        return render_template("intro.html", trial_count=len(TRIALS))

    @app.post("/start")
    def start():
        participant_code = request.form.get("participant_code", "").strip()
        if not participant_code:
            participant_code = f"anon-{secrets.token_hex(4)}"
        if not PARTICIPANT_CODE_PATTERN.fullmatch(participant_code):
            return render_template(
                "intro.html",
                trial_count=len(TRIALS),
                error="The participant code may contain only letters, numbers, hyphens, and underscores.",
            ), 400
        session.clear()
        session["participant_code"] = participant_code
        return redirect(url_for("experiment", trial_index=0))

    @app.get("/stimulus/<int:trial_index>.png")
    def stimulus(trial_index: int):
        if not 0 <= trial_index < len(TRIALS):
            abort(404)
        field = build_scalar_field(trial_index)
        cmap = matplotlib.colormaps[TRIALS[trial_index]["colormap"]]
        rgba = cmap(field.astype(np.float32) / 1000.0, bytes=True)
        image = Image.fromarray(rgba[:, :, :3], mode="RGB")
        payload = io.BytesIO()
        image.save(payload, format="PNG", optimize=True)
        payload.seek(0)
        return send_file(payload, mimetype="image/png", max_age=3600)

    @app.get("/experiment/<int:trial_index>")
    def experiment(trial_index: int):
        if "participant_code" not in session:
            return redirect(url_for("intro"))
        if not 0 <= trial_index < len(TRIALS):
            return redirect(url_for("thanks"))
        trial = TRIALS[trial_index]
        return render_template(
            "experiment.html",
            trial_index=trial_index,
            trial_count=len(TRIALS),
            targets=TARGET_VALUES,
            field_width=FIELD_WIDTH,
            field_height=FIELD_HEIGHT,
            legend_css=colormap_css(trial["colormap"]),
        )

    @app.post("/experiment/<int:trial_index>")
    def submit_experiment(trial_index: int):
        participant_code = session.get("participant_code")
        if not participant_code:
            return redirect(url_for("intro"))
        if not 0 <= trial_index < len(TRIALS):
            abort(404)

        try:
            points = validate_points(request.form.get("points_json", ""))
        except ValueError as exc:
            return str(exc), 400

        field = build_scalar_field(trial_index)
        observed_values = [int(field[y, x]) for x, y in points]
        absolute_errors = [
            abs(observed - target)
            for observed, target in zip(observed_values, TARGET_VALUES)
        ]
        trial = TRIALS[trial_index]
        append_result(
            Path(app.config["RESULTS_PATH"]),
            {
                "response_id": secrets.token_hex(8),
                "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
                "participant_code": participant_code,
                "trial_index": trial_index,
                "seed": trial["seed"],
                "colormap": trial["colormap"],
                "points_json": json.dumps(points, separators=(",", ":")),
                "observed_values_json": json.dumps(observed_values, separators=(",", ":")),
                "absolute_errors_json": json.dumps(absolute_errors, separators=(",", ":")),
            },
        )

        next_trial = trial_index + 1
        if next_trial >= len(TRIALS):
            return redirect(url_for("thanks"))
        return redirect(url_for("experiment", trial_index=next_trial))

    @app.get("/thanks")
    def thanks():
        if "participant_code" not in session:
            return redirect(url_for("intro"))
        return render_template("thanks.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=os.environ.get("FLASK_DEBUG") == "1")
