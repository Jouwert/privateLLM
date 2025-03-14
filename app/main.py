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
