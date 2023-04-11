import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.env_loader import EMAIL_PASSWORD, EMAIL

if EMAIL_PASSWORD is None or EMAIL is None:
    raise BaseException("Missing env variables EMAIL_PASSWORD or EMAIL")


def send_email(to, subject, body):
    # create a message
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # send the message
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, EMAIL_PASSWORD)
    server.sendmail(EMAIL, to, msg.as_string())
    server.quit()
