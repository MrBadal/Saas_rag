FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck support
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model during build (cached in image)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY app.py .

EXPOSE 8001

CMD ["python", "app.py"]
