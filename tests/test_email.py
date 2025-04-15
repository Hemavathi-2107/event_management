# test_email.py
import pytest
from unittest.mock import patch, AsyncMock
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager

@pytest.mark.asyncio
async def test_send_markdown_email():
    # Test data for user email
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }

    # Mock TemplateManager
    mock_template_manager = AsyncMock(spec=TemplateManager)
    mock_template_manager.render_template.return_value = "<html>Mocked Email Content</html>"

    # Patch the SMTPClient to mock send_email method with AsyncMock
    with patch("app.utils.smtp_connection.SMTPClient.send_email", new_callable=AsyncMock) as mock_send_email:
        # Initialize the EmailService with the mocked template manager
        email_service = EmailService(mock_template_manager)

        # Call the method to send the email
        await email_service.send_user_email(user_data, 'email_verification')

        # Assert send_email was called correctly (mocked async call)
        mock_send_email.assert_awaited_once_with(
            "Verify Your Account",
            "<html>Mocked Email Content</html>",
            "test@example.com"
        )
