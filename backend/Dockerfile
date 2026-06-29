FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for some Python audio/math modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies (CPU versions where applicable to keep image size small)
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ /app/backend/
COPY data/ /app/data/
COPY vectorstore/ /app/vectorstore/

ENV FLASK_APP=backend/app.py
ENV PYTHONPATH=/app/backend

EXPOSE 5000

CMD ["python", "backend/app.py"]
