from config import get_settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

settings = get_settings()

class EmailService:
    def send_email(
            self,
            receiver_email: str,
    ):
        sender_email = "syw5141@gmail.com"
        password = settings.email_password

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "회원 가입을 환영합니다."

        body = "TIL 서비스를 이용해주셔서 감사합니다."
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(message)