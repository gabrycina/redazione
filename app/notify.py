import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotifier:
    def __init__(
        self,
        smtp_user: str,
        password: str,
        default_subject: str = "Your daily report",
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465,
    ):
        self.smpt_user = smtp_user
        self.password = password
        self.smpt_server = smtp_server
        self.smpt_port = smtp_port
        self.default_subject = default_subject

    def notify(self, body: str, to_email: str, subject: str = None):
        msg = MIMEMultipart()
        msg["From"] = self.smpt_user
        msg["To"] = to_email
        msg["Subject"] = subject if subject else self.default_subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP_SSL(self.smpt_server, self.smpt_port)
            server.login(self.smpt_user, self.password)
            server.sendmail(self.smpt_user, to_email, msg.as_string())
            server.quit()
            print(f"Email sent successfully to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")
