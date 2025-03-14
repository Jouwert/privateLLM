FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# Set non-root user
RUN useradd -m -u 1000 llmuser

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip git curl \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=llmuser:llmuser . .

# Create model directory
RUN mkdir -p models

# Expose API port
EXPOSE 8080

# Set environment variables
ENV MODEL_PATH=/app/models/model.gguf
ENV API_HOST=0.0.0.0
ENV API_PORT=8080
ENV LOG_LEVEL=INFO

# Switch to non-root user
USER llmuser

# Run application
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
