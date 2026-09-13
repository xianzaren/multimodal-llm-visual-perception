import csv
import json

from questionnaire_app.app import create_app


def make_app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-key",
            "RESULTS_PATH": str(tmp_path / "responses.csv"),
        }
    )


def test_complete_first_trial(tmp_path):
    app = make_app(tmp_path)
    client = app.test_client()

    assert client.get("/").status_code == 200
    start = client.post("/start", data={"participant_code": "P014"})
    assert start.status_code == 302
    assert start.headers["Location"].endswith("/experiment/0")

    stimulus = client.get("/stimulus/0.png")
    assert stimulus.status_code == 200
    assert stimulus.content_type == "image/png"

    points = [{"x": 0, "y": 0}] * 5
    submitted = client.post(
        "/experiment/0",
        data={"points_json": json.dumps(points)},
    )
    assert submitted.status_code == 302
    assert submitted.headers["Location"].endswith("/experiment/1")

    with (tmp_path / "responses.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["participant_code"] == "P014"
    assert rows[0]["trial_index"] == "0"


def test_rejects_out_of_bounds_points(tmp_path):
    app = make_app(tmp_path)
    client = app.test_client()
    client.post("/start", data={"participant_code": "P014"})

    points = [{"x": 9999, "y": 0}] * 5
    response = client.post(
        "/experiment/0",
        data={"points_json": json.dumps(points)},
    )
    assert response.status_code == 400
