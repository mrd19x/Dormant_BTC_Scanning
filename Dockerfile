# Menggunakan image Python versi 3.9 sebagai base image
FROM python:3.9

# Set folder kerja di dalam container
WORKDIR /app

# Install pip secara eksplisit untuk memastikan pip sudah terupdate (opsional)
RUN python -m ensurepip --upgrade && \
    pip install --upgrade pip

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Install dependencies dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file project dari direktori saat ini ke /app di dalam container
COPY . .

# Tentukan perintah yang akan dijalankan saat container dijalankan
CMD ["python3", "scanning.py"]
