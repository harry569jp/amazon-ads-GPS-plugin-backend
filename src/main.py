from fastapi import FastAPI, Depends, HTTPException, status
from fastapi import BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import text

from . import models, auth, database, verification, email_service
from .config import ALLOWED_ORIGINS

# 创建数据库表
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Plugin Backend API",
    description="为溯源插件提供用户认证和数据服务的后端。",
    version="1.0.0",
)

# --- CORS 配置 ---
# 关键修复：在开发环境中，为了解决CORS问题，我们暂时允许所有来源。
# 这修复了浏览器插件由于同源策略限制而无法访问API的问题。
# 注意：在生产环境中，出于安全考虑，应将 "*" 替换为您的Chrome插件的特定来源(e.g., "chrome-extension://your_extension_id")。
origins = ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup: ensure DB migrations (add subscription_level) ---
@app.on_event("startup")
def ensure_db_schema():
    try:
        with database.engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE plugin_users
                ADD COLUMN IF NOT EXISTS subscription_level VARCHAR DEFAULT 'free'
            """))
            conn.commit()
    except Exception as e:
        # 不阻塞启动，但打印日志便于排查
        print("[Startup] Ensure schema error:", e)

# --- Request Models ---
class EmailSchema(BaseModel):
    email: EmailStr

# --- API Endpoints ---

@app.post("/api/send-verification-code", summary="发送邮箱验证码")
def send_code(request: EmailSchema, db: Session = Depends(database.get_db)):
    # 检查邮箱是否已被注册
    db_user = auth.get_user_by_email(db, email=request.email)
    if db_user:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
        
    # 生成、存储并发送验证码
    code = verification.generate_code()
    verification.store_code(request.email, code)
    
    # 尝试发送邮件，如果失败则打印到控制台
    try:
        email_service.send_verification_code(request.email, code)
        print(f"验证码已发送到 {request.email}")
    except Exception as e:
        print(f"邮件发送失败: {e}")
        print(f"向 {request.email} 发送的验证码是: {code}")

    return {"message": "验证码已发送，请查收。"}


@app.post("/api/register", summary="用户注册")
def register_user(user: models.UserCreate, db: Session = Depends(database.get_db)):
    # 验证验证码
    if not verification.verify_code(user.email, user.verification_code):
        raise HTTPException(status_code=400, detail="验证码不正确或已过期")

    # 验证通过，继续创建用户
    db_user = auth.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    return auth.create_user(db=db, user=user)


@app.post("/api/login", summary="用户登录获取Token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", summary="获取当前用户信息")
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user


# --- Subscription (Mock) ---
class SubscriptionUpdate(BaseModel):
    level: str

@app.post("/api/subscription/upgrade-mock", summary="测试用：将当前用户订阅升级为指定等级")
def upgrade_subscription_mock(payload: SubscriptionUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    valid_levels = {"free", "pro"}
    if payload.level not in valid_levels:
        raise HTTPException(status_code=400, detail="无效的订阅等级")
    user = auth.get_user_by_email(db, email=current_user.email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.subscription_level = payload.level
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "订阅已更新", "subscription_level": user.subscription_level}
