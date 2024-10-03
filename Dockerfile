# Gunakan image python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

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
