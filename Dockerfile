# 使用官方Python 3.11 slim版本作为基础镜像
FROM python:3.11-slim

# 在容器内创建一个工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖，--no-cache-dir 选项可以减小镜像体积
RUN pip install --no-cache-dir -r requirements.txt

# 复制所有项目文件到工作目录
COPY . .

# 将/app目录添加到Python模块搜索路径
ENV PYTHONPATH=/app

# 声明容器对外暴露的端口
EXPOSE 8000

# 容器启动时执行的命令（优先使用平台提供的 PORT 环境变量，默认8000）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
