import smtplib
from email.mime.text import MIMEText
import os
import logging

email_success_template = """
안녕하세요? 문화해설사 예약이 완료되었습니다.

1. 신청 내용: 
{application_form}

2. 문화해설사 정보:
👤 이름: {docent_name}
📧 연락처: {docent_email}
🔴 부득이한 사정으로 예약 취소 시 방문일 전일까지 문화해설사님 이메일로 통지 부탁드립니다.

3. 만날 장소: 
🏛 국립중앙박물관 1층 기획전시실 앞

✨ 유익하고 즐거운 시간되시길 바랍니다. 감사합니다!
""".strip()

email_fail_template = """
안녕하세요? 문화해설 예약 프로그램 관리자입니다.

다음의 사유로 문화해설 프로그램 예약이 실패했습니다. 

🔴 실패 사유: {failure_message}

추가적인 문의사항 있으시면 이 메일 주소로 [답장] 부탁드립니다.
""".strip()


def send_mail(sender: str, receiver: str, cc: str, subject: str, body: str) -> None:
    recipients = [receiver, cc]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = receiver
    msg["Cc"] = cc

    # Gmail SMTP: smtp.gmail.com, 포트 587(STARTTLS) 사용
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.ehlo()  # 서버 연결 식별
    smtp_server.starttls()  # TLS(보안) 연결 시작
    smtp_server.login(sender, os.getenv("SMTP_KEY"))

    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()
    logging.info("메일 전송 완료")


def send_success_mail(application_form: str, receiver: str, bot_response: dict) -> None:
    body = email_success_template.format(
        application_form=application_form,
        docent_name=bot_response["docent_name"],
        docent_email=bot_response["docent_email"],
    )
    sender = os.getenv("SENDER_EMAIL")
    subject = "문화해설사 예약이 완료되었습니다."
    cc = bot_response["docent_email"]
    send_mail(sender, receiver, cc, subject, body)


def send_fail_mail(receiver: str, failure_message: str) -> None:
    body = email_fail_template.format(failure_message=failure_message)
    sender = os.getenv("SENDER_EMAIL")
    subject = "문화해설사 예약이 실패했습니다."
    cc = os.getenv("MANAGER_EMAIL")
    send_mail(sender, receiver, cc, subject, body)
