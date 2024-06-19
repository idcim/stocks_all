# 选择基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露容器端口(如果需要)
EXPOSE 8000

# 设置容器启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
