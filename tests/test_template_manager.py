import pytest
from unittest.mock import patch, mock_open
from app.utils.template_manager import TemplateManager


@pytest.fixture
def template_manager():
    return TemplateManager()


@pytest.fixture
def mock_templates():
    return {
        'header.md': "# Welcome\n",
        'footer.md': "\n<footer>Thanks for reading</footer>",
        'welcome.md': "Hello, {name}! Welcome to {platform}."
    }


def test_render_template_success(template_manager, mock_templates):
    m_open = mock_open()
    
    # Side effect to return different content depending on the file name
    def mocked_open(file, *args, **kwargs):
        filename = file.name if hasattr(file, 'name') else str(file)
        for name, content in mock_templates.items():
            if name in filename:
                return mock_open(read_data=content).return_value
        raise FileNotFoundError(f"File {file} not mocked")

    with patch("builtins.open", new=mocked_open):
        html = template_manager.render_template("welcome", name="Hemavathi", platform="FastAPI")

    assert "<h1 style=" in html  # check styled header
    assert "Hemavathi" in html
    assert "FastAPI" in html
    assert "<footer style=" in html
    assert "Thanks for reading" in html
    assert "<div style=" in html  # body style


def test_missing_template_file(template_manager):
    with patch("builtins.open", side_effect=FileNotFoundError("Not found")):
        with pytest.raises(FileNotFoundError):
            template_manager.render_template("welcome", name="Missing", platform="Oops")


def test_invalid_format_keys(template_manager, mock_templates):
    def mocked_open(file, *args, **kwargs):
        filename = file.name if hasattr(file, 'name') else str(file)
        for name, content in mock_templates.items():
            if name in filename:
                return mock_open(read_data=content).return_value
        raise FileNotFoundError

    with patch("builtins.open", new=mocked_open):
        with pytest.raises(KeyError):
            template_manager.render_template("welcome", platform="FastAPI")  # Missing "name"
