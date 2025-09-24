# email_service.py
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import urllib.request
from .config import RESEND_API_KEY, SENDGRID_API_KEY, SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD

# --- 模拟邮件配置 ---
# 警告：请不要将真实的密码硬编码在此处。
# 在生产环境中，请使用环境变量或安全的配置管理工具。
SMTP_SERVER = SMTP_SERVER
SMTP_PORT = SMTP_PORT
SMTP_USERNAME = SMTP_USERNAME
SMTP_PASSWORD = SMTP_PASSWORD

def send_verification_code(recipient_email: str, code: str):
    """
    发送验证码邮件。
    """
    subject = "您的注册验证码"
    body = f"您好，\n\n感谢您注册！您的验证码是：{code}\n\n此验证码将在10分钟后失效。\n\n如果您没有请求此验证码，请忽略此邮件。\n\n祝好！"
    
    # 1) 优先 Resend API（免费额度友好）
    if RESEND_API_KEY:
        try:
            data = {
                "from": "Plugin <no-reply@yourdomain.dev>",
                "to": [recipient_email],
                "subject": subject,
                "text": body
            }
            req = urllib.request.Request(
                url="https://api.resend.com/emails",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {RESEND_API_KEY}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status >= 200 and resp.status < 300:
                    print(f"验证码邮件已成功发送到: {recipient_email} (Resend)")
                    return True
                else:
                    raise Exception(f"Resend status: {resp.status}")
        except Exception as e:
            print("Resend 发送失败，降级到下一通道：", e)

    # 2) 其次 SendGrid API
    if SENDGRID_API_KEY:
        try:
            data = {
                "personalizations": [{"to": [{"email": recipient_email}]}],
                "from": {"email": "no-reply@yourdomain.dev"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}]
            }
            req = urllib.request.Request(
                url="https://api.sendgrid.com/v3/mail/send",
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {SENDGRID_API_KEY}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                if 200 <= resp.status < 300:
                    print(f"验证码邮件已成功发送到: {recipient_email} (SendGrid)")
                    return True
                else:
                    raise Exception(f"SendGrid status: {resp.status}")
        except Exception as e:
            print("SendGrid 发送失败，降级到SMTP：", e)

    # 3) 最后回退 SMTP
    try:
        # 创建邮件消息
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient_email
        
        # 连接SMTP服务器并发送邮件
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # 启用TLS加密
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"验证码邮件已成功发送到: {recipient_email} (SMTP)")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {e}")
        # 如果发送失败，打印到控制台作为备用方案
        print("--- 发送邮件（备用方案）---")
        print(f"收件人: {recipient_email}")
        print(f"主题: {subject}")
        print(f"内容: {body}")
        print("-----------------------")
        raise e


