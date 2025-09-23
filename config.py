# config.py
import os

# 使用环境变量，避免将敏感信息写入代码库/镜像
DATABASE_URL = os.getenv("DATABASE_URL", "")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-env")

# 允许的跨域来源，逗号分隔，例如："https://your-app.deta.dev,chrome-extension://<EXT_ID>"
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",") if o.strip()]

# 邮件服务优先顺序：RESEND > SENDGRID > SMTP
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
