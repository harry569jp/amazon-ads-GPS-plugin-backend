
# verification.py
import random
import string
from datetime import datetime, timedelta

# 使用字典作为内存中的临时存储。在生产环境中，建议使用Redis。
verification_codes = {}

CODE_EXPIRATION_MINUTES = 10

def generate_code(length: int = 6) -> str:
    """生成一个指定长度的随机数字验证码"""
    return "".join(random.choices(string.digits, k=length))

def store_code(email: str, code: str):
    """存储验证码和过期时间"""
    expiration = datetime.now() + timedelta(minutes=CODE_EXPIRATION_MINUTES)
    verification_codes[email] = {"code": code, "expires_at": expiration}
    print(f"为 {email} 存储的验证码: {code}") # 方便调试

def verify_code(email: str, code: str) -> bool:
    """验证用户提交的验证码"""
    stored_data = verification_codes.get(email)
    if not stored_data:
        return False
    
    # 检查是否过期
    if datetime.now() > stored_data["expires_at"]:
        # 清除过期的验证码
        del verification_codes[email]
        return False
        
    # 检查验证码是否匹配
    if stored_data["code"] == code:
        # 验证成功后立即删除，防止重用
        del verification_codes[email]
        return True
        
    return False
