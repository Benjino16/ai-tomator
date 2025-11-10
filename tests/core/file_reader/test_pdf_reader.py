from unittest.mock import patch, MagicMock
from ai_tomator.core.file_reader.pdf_reader import PDFReader


@patch("ai_tomator.core.file_reader.pdf_reader.PdfReader")
def test_pdf_reader_concatenates_text(mock_pdfreader, tmp_path):
    """Verify that PDFReader reads and concatenates text from all pages."""
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Hello"
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "World"
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page1, mock_page2]
    mock_pdfreader.return_value = mock_reader

    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")

    reader = PDFReader()
    text = reader.read(str(pdf_path))

    assert text == "HelloWorld"
    mock_pdfreader.assert_called_once()


@patch("ai_tomator.core.file_reader.pdf_reader.PdfReader")
def test_pdf_reader_returns_empty_if_no_text(mock_pdfreader, tmp_path):
    """Reader should return empty string if no text is extracted."""
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None
    mock_reader = MagicMock()
    mock_reader.pages = [mock_page]
    mock_pdfreader.return_value = mock_reader

    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%EOF")

    reader = PDFReader()
    text = reader.read(str(pdf_path))

    assert text == ""
