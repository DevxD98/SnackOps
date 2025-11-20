from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import shutil
import os
import uuid
from adk_agent.chefbyte_agent import ChefByteADKAgent

app = FastAPI(title="ChefByte API", description="API for ChefByte AI Meal Planner")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent
try:
    agent = ChefByteADKAgent()
    print("✅ ChefByte Agent Initialized")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    agent = None

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MealPlanRequest(BaseModel):
    ingredients: List[str]
    dietary_constraints: Optional[List[str]] = []
    calorie_target: Optional[int] = None
    meal_count: int = 3
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    success: bool

# Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_status": "active" if agent else "inactive"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    session_id = request.session_id or str(uuid.uuid4())
    
    try:
        result = await agent.run_async(request.message, session_id=session_id)
        return {
            "response": result.get("response", "No response generated"),
            "session_id": session_id,
            "success": result.get("success", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), session_id: Optional[str] = None):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Save uploaded file temporarily
    temp_filename = f"temp_{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join("temp_uploads", temp_filename)
    os.makedirs("temp_uploads", exist_ok=True)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process image
        session_id = session_id or str(uuid.uuid4())
        result = agent.process_image(temp_path, query="Analyze this image and list ingredients.")
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "response": result.get("response", ""),
            "session_id": session_id,
            "success": result.get("success", False)
        }
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan-meals")
async def plan_meals(request: MealPlanRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = agent.create_meal_plan(
            ingredients=request.ingredients,
            dietary_constraints=request.dietary_constraints,
            calorie_target=request.calorie_target,
            meal_count=request.meal_count
        )
        return {
            "response": result.get("response", ""),
            "success": result.get("success", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
