# Gunakan image Python 3.11 slim sebagai base image
FROM python:3.11-slim

# Set direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Instal dependencies menggunakan requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori lokal ke dalam container
COPY . .

# Instal dependencies yang diperlukan
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev && \
    pip install --no-cache-dir coincurve rich pycryptodome && \
    apt-get remove -y build-essential libssl-dev && \
    apt-get autoremove -y && \
    apt-get clean

# Eksekusi script Python
CMD ["python", "scanner.py"]
