import smtplib
from email.mime.text import MIMEText

SMTP_EMAIL = "zeph.cael@gmail.com"
SMTP_PASSWORD = "yxnskpumrhxaoqqe"

def send_email(to, subject, content):
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
