from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
from typing import List


class Emailer:

    def __init__(self, sender, password):
        self.sender = sender
        self.password = password

    def send_email(self, to: List[str], subject: str, content: str, host: str = 'smtp.gmail.com', port: int = 465,
                   content_type: str = 'html', encode: str = 'utf-8'):
        sender = self.sender
        password = self.password

        message = MIMEMultipart()
        message['From'] = Header(sender)
        message['To'] = Header(','.join(to))
        message['Subject'] = Header(subject)
        message.attach(MIMEText(content, content_type, encode))

        server = smtplib.SMTP_SSL(host, port)
        server.login(sender, password)
        server.sendmail(sender, to, message.as_string())
        server.quit()
