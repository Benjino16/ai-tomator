import json
import pandas as pd
import pytest
from ai_tomator.core.exporter.expanded_mode import ExpandedExportMode


@pytest.fixture
def exporter():
    return ExpandedExportMode()


def csv_to_df(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(pd.io.common.StringIO(csv_text))


def test_list_of_objects(exporter):
    data = [
        {
            "model": "gemini",
            "temp": 1.0,
            "output": json.dumps(
                [
                    {"id": "1", "answer": False, "quote": "A"},
                    {"id": "2", "answer": True, "quote": "B"},
                ]
            ),
        }
    ]
    df = csv_to_df(exporter.to_csv(data))

    assert len(df) == 2
    assert set(df.columns) == {"model", "temp", "id", "answer", "quote"}
    assert df["id"].astype(str).tolist() == ["1", "2"]
    assert df["answer"].tolist() == [False, True]


def test_dict_output(exporter):
    data = [{"model": "gpt", "output": json.dumps({"x": 5, "y": "ok"})}]
    df = csv_to_df(exporter.to_csv(data))

    assert len(df) == 1
    assert set(df.columns) == {"model", "x", "y"}
    assert df.iloc[0]["x"] == 5
    assert df.iloc[0]["y"] == "ok"


def test_primitive_output(exporter):
    data = [{"id": 1, "output": json.dumps("simple string")}]
    df = csv_to_df(exporter.to_csv(data))

    assert len(df) == 1
    assert "value" in df.columns
    assert df.iloc[0]["value"] == "simple string"


def test_invalid_json(exporter):
    data = [{"id": 2, "output": "{not valid json}"}]
    df = csv_to_df(exporter.to_csv(data))

    assert "_output_raw" in df.columns
    assert df.iloc[0]["_output_raw"] == "{not valid json}"


def test_missing_output_field(exporter):
    data = [{"id": 3, "model": "ollama"}]
    df = csv_to_df(exporter.to_csv(data))

    assert len(df) == 1
    assert "model" in df.columns
    assert "id" in df.columns
    # default empty JSON gives no added fields
    assert set(df.columns) == {"id", "model"}
