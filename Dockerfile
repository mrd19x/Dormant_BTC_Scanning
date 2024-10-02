# Menggunakan base image Python 3.9 sebagai dasar
FROM python:3.9

# Set folder kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Salin semua file project ke dalam container
COPY . .
