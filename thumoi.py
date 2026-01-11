import json
import os
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, TemplateError

# Load .env (EMAIL_SENDER và EMAIL_PASSWORD - dùng App Password nếu có 2FA)
load_dotenv()

EMAIL = os.getenv("EMAIL_SENDER")
PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL or not PASSWORD:
    raise ValueError("EMAIL_SENDER hoặc EMAIL_PASSWORD chưa được set trong .env!")

SUBJECT = "Thư mời tham gia sự kiện"

# Đường dẫn thư mục chứa thumoi.html và thumoi.json
BASE_DIR = r"D:/Module_3/thumoi"  # dùng raw string để tránh lỗi \

# Load JSON
json_path = os.path.join(BASE_DIR, "thumoi.json")
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Không tìm thấy file JSON: {json_path}")

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)  # Đổi tên biến thành data cho phù hợp hơn (không còn là "student")

print("Dữ liệu thư mời:", data)  # Debug để kiểm tra

# Setup Jinja2
env = Environment(loader=FileSystemLoader(BASE_DIR))
try:
    template = env.get_template("thumoi.html")
    html_content = template.render(**data)
except TemplateError as e:
    print("Lỗi render Jinja2:", e)
    raise

# Kết nối SMTP Gmail
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Bật TLS
    server.login(EMAIL, PASSWORD)
    print("Login Gmail thành công!")

    # Tạo email
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Ban Tổ Chức <{EMAIL}>"
    msg["To"] = data["email"]
    msg["Subject"] = SUBJECT

    text_part = MIMEText(
        f"Kính gửi {data.get('ten_nguoi_tham_gia', 'Quý vị')},\n\n"
        f"Ban Tổ Chức trân trọng kính mời quý vị tham gia sự kiện:\n"
        f"- Tên sự kiện: {data.get('ten_su_kien', 'Sự kiện cộng đồng')}\n"
        f"- Thời gian: {data.get('thoi_gian', 'Chưa xác định')}\n"
        f"- Địa điểm: {data.get('dia_diem', 'Chưa xác định')}\n"
        f"- Tổ chức bởi: {data.get('to_chuc', 'Ban Tổ Chức')}\n\n"
        f"Đây là cơ hội tuyệt vời để kết nối cộng đồng, học hỏi và chia sẻ kinh nghiệm.\n"
        f"Vui lòng sắp xếp thời gian tham dự và xác nhận sớm nếu có thể.\n"
        f"Chi tiết trang trọng và đẹp hơn xem trong phần HTML đính kèm.\n\n"
        f"Rất mong được đón tiếp quý vị!\n\n"
        f"Trân trọng,\n"
        f"{data.get('nguoi_gui', 'Ban Tổ Chức')}\n"
        f"{data.get('chuc_vu_nguoi_gui', '')}",
        "plain", "utf-8"
    )

    html_part = MIMEText(html_content, "html", "utf-8")

    msg.attach(text_part)
    msg.attach(html_part)

    # Gửi
    server.sendmail(EMAIL, data["email"], msg.as_string())
    print(f"✅ Đã gửi thư mời thành công đến: {data['email']}")

except smtplib.SMTPAuthenticationError:
    print("Lỗi xác thực: Kiểm tra App Password hoặc bật 2FA + tạo App Password mới!")
except Exception as e:
    print("Lỗi khi gửi email:", str(e))

finally:
    server.quit()