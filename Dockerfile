# Gunakan base image Python yang ringan
FROM python:3.11-slim

# Setel direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Update package manager dan install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Salin semua file ke dalam container
COPY . .

# Gunakan entrypoint untuk menjalankan script
ENTRYPOINT ["python", "scanner.py"]
