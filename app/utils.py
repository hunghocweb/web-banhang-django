import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load biến môi trường khi module được import
load_dotenv()

def send_email(receiver_email,id_item):
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("APP_PASSWORD")

    # Tạo đối tượng MIMEMultipart để chứa nội dung email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Cảm ơn quý khách đã mua hàng - Mời đánh giá sản phẩm"
    message["From"] = sender_email
    message["To"] = receiver_email
    link = ""
    for i in id_item:
        link = f'<a href="http://127.0.0.1:8000/detail_page/?id={i}">Sản phẩm {i}</a>'+"<br>"+link
    # Nội dung email dạng HTML
    html = f"""\
    <html>
    <body>
        <p>Chào quý khách,</p>
        <p>Cảm ơn quý khách đã mua hàng tại Cửa hàng điện tử của chúng tôi.</p>
        <p>Chúng tôi rất mong nhận được phản hồi của quý khách về sản phẩm vừa mua.</p>
        <p>Vui lòng truy cập đường dẫn sau để đánh giá sản phẩm:<br>{link}</p>
        <p>Trân trọng,<br>Hùng - Chủ cửa hàng</p>
    </body>
    </html>
    """
    # Đính kèm nội dung email
    part1 = MIMEText(html, "html")
    message.attach(part1)
    try:
        # Gửi email qua SMTP của Gmail với kết nối SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email đã được gửi thành công!")
    except Exception as e:
        print("Gửi email thất bại:", e)
