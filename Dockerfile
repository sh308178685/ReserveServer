# Dockerfile
# 使用官方Python镜像作为基础镜像
FROM python:3.10-slim

# 设置容器内的工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器内工作目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 声明容器运行时监听的端口
EXPOSE 5000

# 运行Flask应用
CMD ["python", "./app.py"]