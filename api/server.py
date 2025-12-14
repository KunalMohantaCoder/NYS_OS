"""
FastAPI server for AI engine.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference.inference_engine import InferenceEngine
from assistant.assistant import PersonalAssistant
from contextlib import asynccontextmanager

# Global instances (will be initialized on startup)
inference_engine: Optional[InferenceEngine] = None
assistant: Optional[PersonalAssistant] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize AI components on startup."""
    global inference_engine, assistant
    
    # Paths to model and tokenizer
    model_path = os.getenv("AI_MODEL_PATH", "data/models/best_model.pt")
    tokenizer_path = os.getenv("AI_TOKENIZER_PATH", "data/models/tokenizer.json")
    
    device = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
    
    try:
        # Initialize inference engine if model exists
        if os.path.exists(model_path) and os.path.exists(tokenizer_path):
            print(f"Loading model from {model_path}")
            inference_engine = InferenceEngine(model_path, tokenizer_path, device=device)
            print("Inference engine loaded successfully")
        else:
            print(f"Model files not found. Model: {model_path}, Tokenizer: {tokenizer_path}")
            print("AI will use rule-based responses only until model is trained.")
            inference_engine = None
    except Exception as e:
        print(f"Error loading inference engine: {e}")
        inference_engine = None
    
    # Initialize assistant
    base_path = os.getenv("ASSISTANT_BASE_PATH", None)
    data_dir = os.getenv("ASSISTANT_DATA_DIR", "data/assistant")
    assistant = PersonalAssistant(base_path=base_path, data_dir=data_dir)
    print("Personal assistant initialized")
    
    yield  # App runs here
    
    # Cleanup (if needed)
    print("Shutting down AI service...")


app = FastAPI(title="NyxOS AI Engine", version="1.0.0", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    use_context: bool = True
    temperature: float = 1.0
    top_k: Optional[int] = None
    top_p: float = 0.9


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    intent: Optional[str] = None
    success: bool = True


class AssistantRequest(BaseModel):
    """Assistant request model."""
    message: str


class AssistantResponse(BaseModel):
    """Assistant response model."""
    intent: str
    success: bool
    message: str
    data: Optional[Any] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "NyxOS AI Engine",
        "status": "running",
        "model_loaded": inference_engine is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": inference_engine is not None}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint - generates AI response.
    
    Args:
        request: Chat request
    
    Returns:
        Chat response
    """
    if not inference_engine:
        raise HTTPException(
            status_code=503,
            detail="AI model not loaded. Please train the model first."
        )
    
    try:
        response = inference_engine.chat(
            request.message,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p
        )
        
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assistant", response_model=AssistantResponse)
async def assistant_endpoint(request: AssistantRequest):
    """
    Assistant endpoint - processes user requests with intent recognition.
    
    Args:
        request: Assistant request
    
    Returns:
        Assistant response
    """
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    try:
        result = assistant.process_request(request.message, inference_engine)
        
        return AssistantResponse(
            intent=result['intent'],
            success=result['success'],
            message=result['message'],
            data=result.get('data')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    
    if not inference_engine:
        await websocket.send_json({
            "error": "AI model not loaded. Please train the model first."
        })
        await websocket.close()
        return
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            if not message:
                continue
            
            # Generate response
            response = inference_engine.chat(
                message,
                temperature=data.get("temperature", 1.0),
                top_k=data.get("top_k"),
                top_p=data.get("top_p", 0.9)
            )
            
            # Send response
            await websocket.send_json({
                "response": response,
                "success": True
            })
    
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.send_json({
            "error": str(e),
            "success": False
        })


@app.post("/context/clear")
async def clear_context():
    """Clear conversation context."""
    if inference_engine:
        inference_engine.clear_context()
        return {"success": True, "message": "Context cleared"}
    return {"success": False, "message": "Inference engine not loaded"}


@app.get("/context/history")
async def get_context_history():
    """Get conversation history."""
    if inference_engine:
        history = inference_engine.get_context_history()
        return {"success": True, "history": history}
    return {"success": False, "history": []}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

