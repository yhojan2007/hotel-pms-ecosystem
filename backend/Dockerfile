FROM python:3.11-slim

WORKDIR /app

# Evita que Python escriba archivos .pyc en disco y desactiva el buffering de stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema necesarias para compilar paquetes si aplica
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código del backend
COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
