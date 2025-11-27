from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import shutil
import os
import uuid
import base64
import tempfile
from adk_agent.chefbyte_agent import ChefByteADKAgent
from adk_agent.tools.recipe_search_adk import search_recipes
from adk_agent.tools.nutrition_estimator_adk import estimate_nutrition
from adk_agent.tools.vision_tool import extract_ingredients_from_image
from adk_agent.tools.genai_recipe_tool import generate_recipe

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

# New models for Chefbyte-UI integration
class UserPreferences(BaseModel):
    diet: str  # 'Vegetarian', 'Vegan', 'Non-Vegetarian', 'Keto', 'Paleo', 'Anything'
    timeLimit: str  # e.g. "45 minutes"
    calories: int
    servings: int

class AnalyzeInputRequest(BaseModel):
    mode: str  # 'image' | 'text'
    data: str  # base64 image or text ingredients
    preferences: UserPreferences
    current_inventory: List[str] = []

class GenerateAlternativesRequest(BaseModel):
    ingredients: List[str]
    preferences: UserPreferences
    exclude_titles: List[str] = []

class ReceiptData(BaseModel):
    storeName: Optional[str] = None
    date: Optional[str] = None
    total: Optional[str] = None

class Nutrition(BaseModel):
    calories: int
    protein: str
    carbs: str
    fats: str

class Recipe(BaseModel):
    id: str
    title: str
    description: str
    time: str
    baseServings: int
    ingredients: List[str]
    steps: List[str]
    nutrition: Nutrition
    matchScore: int

class ChefResponse(BaseModel):
    detectedIngredients: List[str]
    receiptData: Optional[ReceiptData] = None
    reasoning: str
    recipes: List[Recipe]

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

@app.post("/analyze-input", response_model=ChefResponse)
async def analyze_input(request: AnalyzeInputRequest):
    """ADK-backed endpoint: extract ingredients, search dataset recipes, enrich nutrition."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        detected_ingredients: List[str] = []
        receipt_data = None

        # Step 1: Ingredient extraction
        if request.mode == 'image':
            import base64, tempfile
            if ',' in request.data:
                image_data = request.data.split(',')[1]
            else:
                image_data = request.data
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(base64.b64decode(image_data))
                tmp_path = tmp.name
            try:
                vision_result = extract_ingredients_from_image(tmp_path, image_type="fridge")
                if vision_result.get('success'):
                    for item in vision_result.get('ingredients', []):
                        name = item.get('name') if isinstance(item, dict) else item
                        if name:
                            detected_ingredients.append(name.strip())
            finally:
                os.remove(tmp_path)
        else:
            detected_ingredients = [ing.strip() for ing in request.data.split(',') if ing.strip()]

        # Merge with current inventory
        all_ingredients = sorted(set([i.lower() for i in (request.current_inventory + detected_ingredients)]))

        # Use the agentic method - let Gemini decide which tools to use!
        print(f"🤖 Using agentic approach for: {all_ingredients}")
        
        # Create a unique session ID for this request
        import uuid
        session_id = f"analyze_{uuid.uuid4().hex[:8]}"
        
        # Call the agentic method
        result = await agent.analyze_ingredients_agentic(
            ingredients=all_ingredients,
            preferences={
                'diet': request.preferences.diet,
                'timeLimit': request.preferences.timeLimit,
                'calories': request.preferences.calories,
                'servings': request.preferences.servings
            },
            session_id=session_id
        )
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Agent failed'))
        
        # The agent already returns data in the correct format!
        return {
            'detectedIngredients': all_ingredients,
            'receiptData': receipt_data,
            'reasoning': result.get('reasoning', 'Generated recipes using agentic AI'),
            'recipes': result.get('recipes', [])
        }
    except Exception as e:
        print(f"Error in analyze_input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-alternatives", response_model=ChefResponse)
async def generate_alternatives(request: GenerateAlternativesRequest):
    """Return 3 new alternative recipes using ADK recipe search, excluding prior titles."""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        exclude_lower = {t.lower() for t in request.exclude_titles}
        dietary_map = {
            'Vegetarian': ['vegetarian'],
            'Vegan': ['vegan'],
            'Non-Vegetarian': None,
            'Keto': ['keto'],
            'Paleo': ['paleo'],
            'Anything': None
        }
        dietary_constraints = dietary_map.get(request.preferences.diet, None)
        search_result = agent._enhanced_search_recipes(
            available_ingredients=request.ingredients,
            dietary_constraints=dietary_constraints,
            max_missing=2,
            cuisine_type=None
        ) if hasattr(agent, '_enhanced_search_recipes') else search_recipes(
            available_ingredients=request.ingredients,
            dietary_constraints=dietary_constraints,
            max_missing=2,
            cuisine_type=None
        )
        raw = search_result.get('recipes', []) if isinstance(search_result, dict) else []
        filtered = [r for r in raw if r.get('name','').lower() not in exclude_lower]
        if not filtered:
            filtered = raw[:3] if raw else [{
                'name': 'Creative Fusion Bowl',
                'ingredients': request.ingredients[:6],
                'match_score': 70,
                'calories': request.preferences.calories,
                'protein_g': 20,
                'carbs_g': 35,
                'fat_g': 10,
                'prep_time': request.preferences.timeLimit
            }]
        filtered = filtered[:3]
        recipes = []
        for idx, r in enumerate(filtered):
            # Ensure time is a string
            prep_time = r.get('prep_time', request.preferences.timeLimit)
            time_str = str(prep_time) if not isinstance(prep_time, str) else prep_time
            if time_str.isdigit():
                time_str = f"{time_str} minutes"
                
            recipes.append({
                'id': f"alt_{idx+1}_{r.get('name','').lower().replace(' ','_')}",
                'title': r.get('name','Alternative Recipe'),
                'description': 'Alternative recipe suggestion avoiding previous selections',
                'time': time_str,
                'baseServings': request.preferences.servings,
                'ingredients': r.get('ingredients', request.ingredients[:5]),
                'steps': ["Gather ingredients", "Cook appropriately", "Adjust seasoning", "Serve"],
                'nutrition': {
                    'calories': int(r.get('calories', request.preferences.calories)),
                    'protein': f"{r.get('protein_g', 0)}g",
                    'carbs': f"{r.get('carbs_g', 0)}g",
                    'fats': f"{r.get('fat_g', 0)}g"
                },
                'matchScore': int(r.get('match_score', 0))
            })
        reasoning = f"Generated {len(recipes)} new alternatives excluding {len(exclude_lower)} prior titles."
        return {
            'detectedIngredients': request.ingredients,
            'reasoning': reasoning,
            'recipes': recipes
        }
    except Exception as e:
        print(f"Error in generate_alternatives: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
