import pytest
from unittest.mock import patch, MagicMock
from ai_tomator.core.file_reader import read_file

@patch("ai_tomator.core.file_reader.PdfReader")
def test_read_file_with_pypdf2(mock_pdfreader, tmp_path):
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Hello"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "World"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page1, mock_page2]
    mock_pdfreader.return_value = mock_reader


    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")

    text = read_file("pypdf2", str(pdf_path))

    assert text == "HelloWorld"
    mock_pdfreader.assert_called_once()

def test_read_file_invalid_processor():
    with pytest.raises(ValueError):
        read_file("invalid", "file.pdf")
