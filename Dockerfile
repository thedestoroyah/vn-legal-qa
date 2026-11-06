# Image dùng chung cho 2 dịch vụ trong docker-compose.yml; lệnh chạy của mỗi dịch vụ đặt trong compose.
# Chỉ mục, cache mô hình và cache LLM gắn từ máy khi chạy, không nằm trong image.
FROM python:3.14-slim

WORKDIR /app

# torch CPU tách lớp riêng: bản mặc định kéo theo CUDA nặng vài GB; đổi requirements cũng không phải tải lại
RUN pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY eval/ eval/
COPY data/raw/laws.json data/raw/laws.json
COPY data/processed/ data/processed/

ENV PYTHONPATH=/app HF_HOME=/root/.cache/huggingface
