import pytest
from unittest.mock import patch, MagicMock
from app.utils.smtp_connection import SMTPClient


@pytest.fixture
def smtp_client():
    return SMTPClient(server="smtp.example.com", port=587, username="user@example.com", password="securepass")


def test_send_email_success(smtp_client):
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        smtp_client.send_email(
            subject="Test Subject",
            html_content="<p>Hello</p>",
            recipient="receiver@example.com"
        )

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@example.com", "securepass")
        mock_server.sendmail.assert_called_once()


def test_send_email_failure(smtp_client, caplog):
    with patch("smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.login.side_effect = Exception("Login failed")

        with pytest.raises(Exception, match="Login failed"):
            smtp_client.send_email(
                subject="Test Fail",
                html_content="<p>Fail</p>",
                recipient="fail@example.com"
            )

        assert "Failed to send email: Login failed" in caplog.text
