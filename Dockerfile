# 使用官方 Python 3.8 slim 镜像
FROM python:3.10-slim

# 设置容器内的工作目录
WORKDIR /app

# 将 requirements.txt 文件复制到工作目录
COPY requirements.txt .

# 安装系统依赖项并安装Python包
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmariadb-dev-compat \
    pkg-config \
    libiodbc2-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 将应用源代码复制到工作目录
COPY . .

# 声明容器运行时监听的端口
EXPOSE 5000

# 运行 Flask 应用
CMD ["python", "./app.py"]