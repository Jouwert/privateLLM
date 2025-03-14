Let's work through setting up the necessary development tools and dependencies for your privateLLM project step by step, specifically for Ubuntu.

### Step 1: Install Python and Development Tools

```bash
# Update package lists
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv build-essential

# Verify installation
python3 --version
pip3 --version
```

### Step 2: Set Up Python Virtual Environment

```bash
# Navigate to your project directory
cd privateLLM

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Your command prompt should now show (venv) at the beginning
```

### Step 3: Create and Fill Requirements File

```bash
# Create requirements.txt file
touch requirements.txt

# Open the file with nano editor
nano requirements.txt
```

Now paste the following content into the file:

```
# LLM libraries
llama-cpp-python==0.2.11
transformers==4.34.0
accelerate==0.23.0

# API and server
fastapi==0.104.0
uvicorn==0.23.2
pydantic==2.4.2

# Utilities
numpy==1.26.0
pandas==2.1.1

# Security
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6

# Monitoring and logging
prometheus-client==0.17.1
loguru==0.7.2
```

Save the file:
- Press `Ctrl+O` to write the file
- Press `Enter` to confirm
- Press `Ctrl+X` to exit nano

### Step 4: Install Dependencies

```bash
# Install the requirements
pip install -r requirements.txt
```

### Step 5: Create Project Directory Structure

```bash
# Create main directories
mkdir -p app/api app/core app/models app/security app/utils
mkdir -p scripts tests/unit tests/integration docs

# Create basic files
touch app/main.py
touch app/api/llm_endpoint.py
touch app/api/auth.py
touch app/models/model_loader.py
touch app/security/auth.py
touch app/utils/logging_config.py
touch tests/conftest.py
```

### Step 6: Install Docker (if not already installed)

```bash
# Remove old versions if they exist
sudo apt remove docker docker-engine docker.io containerd runc

# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update and install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add your user to the docker group to run Docker without sudo
sudo usermod -aG docker $USER

# Verify Docker installation
docker --version
```

Note: You may need to log out and log back in for the group changes to take effect.

### Step 7: Create Docker Configuration Files

```bash
# Create Dockerfile
nano Dockerfile
```

Add the following content:

```dockerfile
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
```

Save and exit nano (Ctrl+O, Enter, Ctrl+X).

Create docker-compose file:

```bash
# Create docker-compose.yml
nano docker-compose.yml
```

Add the following content:

```yaml
version: '3.8'

services:
  llm-api:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./models:/app/models
    environment:
      - MODEL_PATH=/app/models/model.gguf
      - API_HOST=0.0.0.0
      - API_PORT=8080
      - LOG_LEVEL=INFO
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Save and exit nano (Ctrl+O, Enter, Ctrl+X).

### Step 8: Document Your Setup

Create a setup guide:

```bash
# Create setup documentation
nano docs/setup_guide.md
```

Add the following content:

```markdown
# privateLLM Setup Guide

## Prerequisites
- Ubuntu Linux
- Python 3.8+
- Docker and Docker Compose
- NVIDIA GPU (for optimal performance)

## Development Environment Setup

### 1. Install Required Tools

```bash
# Update package lists
sudo apt update

# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv build-essential
```

### 2. Clone and Configure Repository

```bash
# Clone repository
git clone https://github.com/Jouwert/privateLLM.git
cd privateLLM

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Docker Setup

Make sure Docker is installed and running:

```bash
# Verify Docker installation
docker --version
docker-compose --version

# Build Docker image
docker-compose build
```

### 4. Running the Application

#### Development Mode (Local)

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

#### Using Docker

```bash
# Start the application with Docker
docker-compose up

# Run in background
docker-compose up -d
```

### 5. Testing

```bash
# Run tests
pytest
```

## Additional Resources
- Project documentation: [docs/](../docs/)
- Docker documentation: [https://docs.docker.com/](https://docs.docker.com/)
- RunPod documentation: [https://docs.runpod.io/](https://docs.runpod.io/)
```

Save and exit nano (Ctrl+O, Enter, Ctrl+X).

### Step 9: Create a Basic Application Entry Point

```bash
# Create a basic app entry point
nano app/main.py
```

Add the following content:

```python
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
import uvicorn
import os
from loguru import logger

app = FastAPI(title="Private LLM API", description="Secure API for accessing private LLM deployments")

# Configure logging
logger.add("logs/app.log", rotation="500 MB", level=os.getenv("LOG_LEVEL", "INFO"))

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 1024
    temperature: float = 0.7

class QueryResponse(BaseModel):
    text: str
    tokens_used: int

@app.get("/")
async def root():
    return {"status": "ok", "message": "Private LLM API is running"}

@app.post("/api/generate", response_model=QueryResponse)
async def generate(request: QueryRequest):
    try:
        # Placeholder for actual model inference
        # In a real implementation, you would load and call your LLM here
        logger.info(f"Processing prompt: {request.prompt[:20]}...")
        
        # Mock response for now
        response = {
            "text": f"This is a mock response to: {request.prompt}",
            "tokens_used": len(request.prompt.split()) * 2
        }
        
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host=os.getenv("API_HOST", "0.0.0.0"), 
                port=int(os.getenv("API_PORT", 8080)), reload=True)
```

Save and exit nano (Ctrl+O, Enter, Ctrl+X).

### Step 10: Add Your Changes to Git

```bash
# Create logs directory (for the application logs)
mkdir -p logs
touch logs/.gitkeep

# Add a .gitignore file
nano .gitignore
```

Add the following content to .gitignore:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
*.egg-info/

# Logs
logs/*
!logs/.gitkeep

# Model files
models/*
!models/.gitkeep

# Environment variables
.env

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Docker
.docker/

# Test reports
.coverage
htmlcov/
```

Save and exit nano (Ctrl+O, Enter, Ctrl+X).

```bash
# Create model directory
mkdir -p models
touch models/.gitkeep

# Add and commit changes
git add .
git commit -m "Set up development environment and add initial application structure"
git push origin main
```

### Step 11: Verify Your Setup

```bash
# Make sure everything is working
source venv/bin/activate  # If not already activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

This should start a development server. You can access the API documentation at http://localhost:8080/docs in your web browser.

You've now completed setting up your development environment and documenting the procedures. Your next task would be to move on to Phase 1.3 (Security Planning) in your project plan.

When you're using Ubuntu, you should use `pip3` instead of `pip` to ensure you're using the Python 3 version of pip. Let's fix that:

```bash
# Install pip3 if it's not installed
sudo apt install python3-pip

# Then install the requirements using pip3
pip3 install -r requirements.txt
```

Make sure you're in your project directory and have your virtual environment activated:

```bash
# Navigate to your project directory
cd privateLLM

# Activate your virtual environment
source venv/bin/activate

# Now install requirements
pip install -r requirements.txt
```

When your virtual environment is activated, you should see `(venv)` at the beginning of your command prompt. After activating the virtual environment, you can use `pip` instead of `pip3`.
