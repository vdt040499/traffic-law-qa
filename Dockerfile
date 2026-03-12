FROM python:3.10

# Cài đặt thư mục làm việc mặc định trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện Python cần thiết (kể cả AI model và dependencies)
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# HuggingFace Spaces yêu cầu cổng (PORT) mặc định phải là 7860
ENV PORT=7860

# Mở quyền thực thi các file Python
RUN chmod +x src/traffic_law_qa/ui/api.py

# Câu lệnh khởi quay server FastAPI tự động đọc cổng $PORT (7860) lúc nãy tải xong
CMD ["python", "src/traffic_law_qa/ui/api.py"]
