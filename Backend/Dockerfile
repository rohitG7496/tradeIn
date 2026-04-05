FROM python:3.9-slim

# Install system dependencies for MySQL and building Python packages
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Run the application
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "Backend.wsgi:application", "--bind", "0.0.0.0:8000"]
