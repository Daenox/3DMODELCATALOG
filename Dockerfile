FROM python:3.12-slim

WORKDIR /app

# Встановлення системних залежностей для роботи з графікою
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

# Ініціалізація бази даних при білді
RUN python seed_data.py

EXPOSE 5000

# Запуск через gunicorn або waitress
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
