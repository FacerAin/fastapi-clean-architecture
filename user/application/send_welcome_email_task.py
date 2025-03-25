from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from celery import Task
from config import get_settings


settings = get_settings()

class SendWelcomeEmailTask(Task):
    name = "send_welcome_email_task"

    def run(self, receiver_email: str):
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
        
    