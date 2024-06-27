import resend

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
            email: resend.Email = resend.Emails.send(params)
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
