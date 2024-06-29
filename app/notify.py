import resend
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(
        self,
        api_key,
        default_subject: str = "Your daily report",
    ):
        self.default_subject = default_subject
        resend.api_key = api_key

    def notify(self, body: str, to_email: str, subject: str = None):
        params: resend.Emails.SendParams = {
            "from": "redact@mail.redact.lofipapers.com",
            "to": [to_email],
            "subject": subject if subject else self.default_subject,
            "html": body,
            "reply_to": "redazionelofi@gmail.com"
        }

        try:
            resend.Emails.send(params)
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to sent email to {to_email} -- {e}")
