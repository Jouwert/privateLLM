import openi
from transformers import AutoModelForCausalLM, AutoTokenizer
from fastapi import FastAPI
from pydantic import BaseModel

# Load Mistral model and tokenizer
model_name = "Mistral-latest"  # Adjust model name if needed
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# FastAPI app setup
app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate/")
async def generate_response(request: PromptRequest):
    inputs = tokenizer(request.prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"])
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"response": response}

# OpenI UI setup
def run_ui():
    openi.Interface(
        fn=lambda x: tokenizer.decode(model.generate(tokenizer(x)["input_ids"])[0], skip_special_tokens=True),
        inputs="text",
        outputs="text"
    ).launch()

if __name__ == "__main__":
    # Run both the FastAPI server and the OpenI UI
    import threading
    threading.Thread(target=run_ui).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
