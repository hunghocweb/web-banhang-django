import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

# Load biến môi trường khi module được import
load_dotenv()

# Cấu hình logging để in ra console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(receiver_email, id_item):
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("APP_PASSWORD")
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")  # fallback local

    # Tạo email HTML
    message = MIMEMultipart("alternative")
    message["Subject"] = "Cảm ơn quý khách đã mua hàng - Mời đánh giá sản phẩm"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Tạo link sản phẩm
    link_html = ""
    for i in id_item:
        link_html += f'<a href="{BASE_URL}/detail_page/?id={i}">Sản phẩm {i}</a><br>'

    html = f"""
    <html>
    <body>
        <p>Chào quý khách,</p>
        <p>Cảm ơn quý khách đã mua hàng tại Cửa hàng điện tử của chúng tôi.</p>
        <p>Chúng tôi rất mong nhận được phản hồi của quý khách về sản phẩm vừa mua.</p>
        <p>Vui lòng truy cập đường dẫn sau để đánh giá sản phẩm:<br>{link_html}</p>
        <p>Trân trọng,<br>Hùng - Chủ cửa hàng</p>
    </body>
    </html>
    """
    message.attach(MIMEText(html, "html"))

    try:
        # Gửi email qua SMTP của Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender_email, password)
            result = server.sendmail(sender_email, receiver_email, message.as_string())
            if not result:
                logger.info(f"Email accepted by SMTP server for {receiver_email}")
                return {"status": "accepted", "detail": None}
            else:
                logger.error(f"Sendmail returned failures: {result}")
                return {"status": "failed", "detail": result}
    except Exception as e:
        logger.exception("Gửi email thất bại (exception)")
        return {"status": "error", "detail": str(e)}
