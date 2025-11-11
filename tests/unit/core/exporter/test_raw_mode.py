import pandas as pd
import pytest
from ai_tomator.core.exporter.raw_mode import RawExportMode


@pytest.fixture
def exporter():
    return RawExportMode()


def csv_to_df(csv_text: str) -> pd.DataFrame:
    return pd.read_csv(pd.io.common.StringIO(csv_text))


def test_simple_rows(exporter):
    data = [
        {"model": "gemini", "temp": 1.0, "output": "raw text"},
        {"model": "gpt", "temp": 0.7, "output": "another"},
    ]
    df = csv_to_df(exporter.to_csv(data))

    assert len(df) == 2
    assert set(df.columns) == {"model", "temp", "output"}
    assert df["model"].tolist() == ["gemini", "gpt"]
    assert df["temp"].tolist() == [1.0, 0.7]
    assert df["output"].tolist() == ["raw text", "another"]


def test_missing_field(exporter):
    data = [{"model": "ollama"}]
    df = csv_to_df(exporter.to_csv(data))

    assert "model" in df.columns
    assert "output" not in df.columns
    assert df.iloc[0]["model"] == "ollama"


def test_mixed_fields(exporter):
    data = [
        {"model": "openai", "temp": 0.5},
        {"model": "gemini", "engine": "test_engine"},
    ]
    df = csv_to_df(exporter.to_csv(data))

    assert set(df.columns) == {"model", "temp", "engine"}
    assert pd.isna(df.iloc[0]["engine"])
    assert pd.isna(df.iloc[1]["temp"])


def test_special_characters_in_output(exporter):
    data = [{"model": "gemini", "output": "line1\nline2,with,commas"}]
    csv_text = exporter.to_csv(data)
    # Newlines and commas should be quoted
    assert '"' in csv_text or "\n" in csv_text

    df = csv_to_df(csv_text)
    assert df.iloc[0]["output"].startswith("line1")
    assert "line2" in df.iloc[0]["output"]
