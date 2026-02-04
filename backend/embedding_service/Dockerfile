FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck and clean up in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Install dependencies without cache
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt && \
    rm -rf /root/.cache/pip/*

# Download model during build (cached in image)
# Use --no-cache-dir to prevent pip cache
RUN pip install --no-cache-dir sentence-transformers && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" && \
    rm -rf /root/.cache/pip/* /tmp/*

COPY app.py .

EXPOSE 8001

# Use python directly without shell
CMD ["python", "app.py"]
