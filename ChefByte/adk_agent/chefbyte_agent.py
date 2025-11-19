"""
ChefByte ADK Agent - Main orchestrator using Google ADK framework
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types
import yaml
from typing import Dict, List, Any, Optional
import asyncio

# Import our custom tools
from adk_agent.tools import (
    vision_tool,
    recipe_search_tool,
    nutrition_estimator_tool,
    grocery_list_tool
)

# Import persistent memory
from adk_agent.persistent_memory import PersistentMemory


class ChefByteADKAgent:
    """
    Main ChefByte agent using Google Gemini directly (simplified approach)
    
    This agent:
    - Uses Gemini Vision for ingredient extraction
    - Searches recipes based on available ingredients
    - Calculates nutrition and creates meal plans
    - Handles multi-modal input (vision, voice, text)
    - Optimized for Indian households and recipes
    """
    
    def __init__(self, config_path: Optional[str] = None, user_id: str = "default_user"):
        """
        Initialize ChefByte ADK Agent
        
        Args:
            config_path: Path to config.yaml file
            user_id: Unique identifier for the user (for persistent memory)
        """
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                'config.yaml'
            )
        
        self.config = self._load_config(config_path)
        
        # Initialize persistent memory for this user
        self.memory = PersistentMemory(user_id=user_id)
        print(f"📦 Loaded memory for user: {user_id}")
        
        # Load system prompt
        system_prompt = self._load_system_prompt()
        
        # Enhance system prompt with memory context
        memory_context = self.memory.get_agent_context()
        enhanced_prompt = self._enhance_prompt_with_memory(system_prompt, memory_context)
        
        # Initialize Gemini client directly
        # Configure API key
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set")
        
        self.client = genai.Client(api_key=api_key)
        
        # Set up model with tools
        self.model_id = self.config['agent']['model']
        self.system_instruction = enhanced_prompt
        
        # Store conversation history per session
        self.conversation_history = {}
        
        # Convert ADK tools to Gemini function declarations
        self.tools = self._prepare_tools()
        
        # Count actual function declarations
        total_functions = sum(len(tool.function_declarations) for tool in self.tools)
        print(f"✓ ChefByte Agent initialized with {total_functions} tools")
    
    
    def _prepare_tools(self) -> List[types.Tool]:
        """Convert ADK FunctionTools to Gemini tool declarations"""
        # Import the actual functions from our tools
        from adk_agent.tools.vision_tool import extract_ingredients_from_image
        from adk_agent.tools.recipe_search_adk import search_recipes
        from adk_agent.tools.nutrition_estimator_adk import estimate_nutrition
        from adk_agent.tools.grocery_list_tool import generate_grocery_list
        
        # Store function references
        self.tool_functions = {
            'extract_ingredients_from_image': extract_ingredients_from_image,
            'search_recipes': self._enhanced_search_recipes,  # Wrap with enhancement
            'estimate_nutrition': estimate_nutrition,
            'generate_grocery_list': generate_grocery_list
        }
        
        # Store original search function
        self._original_search_recipes = search_recipes
        
        # Return tool declarations for Gemini
        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name='extract_ingredients_from_image',
                        description='Extract ingredients from a fridge photo or receipt image',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'image_path': types.Schema(type=types.Type.STRING, description='Path to the image file'),
                                'image_type': types.Schema(type=types.Type.STRING, description='Type of image: fridge or receipt')
                            },
                            required=['image_path', 'image_type']
                        )
                    ),
                    types.FunctionDeclaration(
                        name='search_recipes',
                        description='Search for recipes matching available ingredients. ALWAYS call this when user mentions ingredients or asks for recipe suggestions, even with just 1-2 ingredients. The system automatically adjusts flexibility based on ingredient count.',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'available_ingredients': types.Schema(type=types.Type.STRING, description='Comma-separated list of available ingredients'),
                                'dietary_constraints': types.Schema(type=types.Type.STRING, description='Dietary constraints (e.g., vegetarian, vegan)'),
                                'max_missing': types.Schema(type=types.Type.INTEGER, description='Maximum missing ingredients allowed (will be auto-adjusted for few ingredients)'),
                                'cuisine_type': types.Schema(type=types.Type.STRING, description='Preferred cuisine type (e.g., indian, punjabi, south_indian)')
                            },
                            required=['available_ingredients']
                        )
                    ),
                    types.FunctionDeclaration(
                        name='estimate_nutrition',
                        description='Calculate nutrition and create meal plan from recipes',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'recipes': types.Schema(type=types.Type.STRING, description='JSON string of recipe list'),
                                'calorie_target': types.Schema(type=types.Type.INTEGER, description='Target daily calories'),
                                'meal_count': types.Schema(type=types.Type.INTEGER, description='Number of meals'),
                                'protein_target': types.Schema(type=types.Type.INTEGER, description='Target protein in grams')
                            },
                            required=['recipes', 'meal_count']
                        )
                    )
                ]
            ),
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name='generate_grocery_list',
                        description='Generate a grocery list from items or meal plan',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'items': types.Schema(
                                    type=types.Type.ARRAY,
                                    items=types.Schema(type=types.Type.STRING),
                                    description='List of items to buy'
                                ),
                                'meal_plan_context': types.Schema(
                                    type=types.Type.STRING,
                                    description='Context about the meal plan'
                                )
                            },
                            required=['items']
                        )
                    )
                ]
            )
        ]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"⚠ Config file not found at {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'agent': {
                'name': 'ChefByte',
                'description': 'AI meal planning agent for Indian households',
                'model': 'gemini-2.5-flash',
                'temperature': 0.7,
                'max_tokens': 2048
            },
            'behavior': {
                'reasoning_style': 'react',
                'max_iterations': 10,
                'verbose': True
            }
        }
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            'prompts',
            'system_prompt.md'
        )
        
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠ System prompt not found at {prompt_path}")
            return "You are ChefByte, an AI meal planning assistant for Indian households."
    
    def _enhance_prompt_with_memory(self, base_prompt: str, memory_context: Dict) -> str:
        """Enhance system prompt with user's memory context"""
        memory_section = f"""

## USER MEMORY CONTEXT

**Current Fridge Inventory** ({memory_context['total_ingredients']} ingredients):
{', '.join(memory_context['fridge_inventory'][:20]) if memory_context['fridge_inventory'] else 'No ingredients stored'}

**Dietary Preferences**:
{', '.join(memory_context['dietary_constraints']) if memory_context['dietary_constraints'] else 'None set'}

**Preferred Cuisines**:
{', '.join(memory_context['cuisine_preferences']) if memory_context['cuisine_preferences'] else 'None set'}

**Calorie Target**: {memory_context['calorie_target'] or 'Not set'}

**Food Allergies**:
{', '.join(memory_context['allergies']) if memory_context['allergies'] else 'None'}

**Recently Cooked** (last 5):
{', '.join(memory_context['recent_recipes']) if memory_context['recent_recipes'] else 'No history'}

**Favorite Recipes**:
{', '.join(memory_context['favorite_recipes'][:10]) if memory_context['favorite_recipes'] else 'None marked'}

**Disliked Recipes** (avoid suggesting these):
{', '.join(memory_context['disliked_recipes']) if memory_context['disliked_recipes'] else 'None'}

---

**IMPORTANT INSTRUCTIONS**:
- When user scans fridge, automatically use those ingredients for recipe suggestions
- Don't suggest recipes from the disliked list
- Prioritize favorite recipes when possible
- Consider dietary constraints in all recommendations
- Track which recipes user cooks for better future suggestions
"""
        
        return base_prompt + memory_section
    
    def run(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent with user input (synchronous wrapper)
        
        Args:
            user_input: User's message or query
            session_id: Optional session ID for conversation continuity
        
        Returns:
            Agent response dictionary
        """
        # Run async version in sync context
        return asyncio.run(self.run_async(user_input, session_id))
    
    async def run_async(self, user_input: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent asynchronously using Gemini with function calling
        
        Args:
            user_input: User's message or query
            session_id: Optional session ID for conversation continuity
        
        Returns:
            Agent response dictionary
        """
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if session_id is None:
                    session_id = "default_session"
                
                # Get or create conversation history for this session
                if session_id not in self.conversation_history:
                    self.conversation_history[session_id] = []
                
                # Add user message to history
                self.conversation_history[session_id].append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_input)]
                    )
                )
                
                # Generate response with tools
                response = await self.client.aio.models.generate_content(
                    model=self.model_id,
                    contents=self.conversation_history[session_id],
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction,
                        tools=self.tools,
                        temperature=0.7
                    )
                )
                
                # Handle function calls if present
                response_parts = []
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            # Execute the function
                            func_name = part.function_call.name
                            func_args = dict(part.function_call.args)
                            
                            # Call the actual function
                            if func_name in self.tool_functions:
                                result = self.tool_functions[func_name](**func_args)
                                
                                # Update persistent memory based on tool used
                                self._update_memory_from_tool(func_name, func_args, result)
                                
                                # Add function response to history
                                self.conversation_history[session_id].append(
                                    types.Content(
                                        role="model",
                                        parts=[types.Part(function_call=part.function_call)]
                                    )
                                )
                                self.conversation_history[session_id].append(
                                    types.Content(
                                        role="function",
                                        parts=[types.Part(
                                            function_response=types.FunctionResponse(
                                                name=func_name,
                                                response={'result': str(result)}
                                            )
                                        )]
                                    )
                                )
                                
                                # Get final response after function execution
                                final_response = await self.client.aio.models.generate_content(
                                    model=self.model_id,
                                    contents=self.conversation_history[session_id],
                                    config=types.GenerateContentConfig(
                                        system_instruction=self.system_instruction,
                                        tools=self.tools,
                                        temperature=0.7
                                    )
                                )
                                
                                if final_response.text:
                                    response_parts.append(final_response.text)
                        elif part.text:
                            response_parts.append(part.text)
                
                # Combine response
                response_text = ''.join(response_parts) if response_parts else response.text or "I processed your request."
                
                # Add assistant response to history
                self.conversation_history[session_id].append(
                    types.Content(
                        role="model",
                        parts=[types.Part(text=response_text)]
                    )
                )
                
                return {
                    "success": True,
                    "response": response_text,
                    "agent_name": self.config['agent']['name'],
                    "session_id": session_id
                }
            
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a 503 overload error
                if '503' in error_str or 'overloaded' in error_str.lower():
                    if attempt < max_retries - 1:
                        print(f"⚠️  Model overloaded, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        return {
                            "success": False,
                            "error": "The Gemini API is currently overloaded. Please try again in a moment.",
                            "response": "Sorry, I'm experiencing high traffic right now. Please try your request again in a few seconds."
                        }
                else:
                    # Other errors
                    import traceback
                    return {
                        "success": False,
                        "error": error_str,
                        "traceback": traceback.format_exc(),
                        "response": None
                    }
        
        return {
            "success": False,
            "error": "Max retries exceeded",
            "response": "Sorry, I couldn't process your request after multiple attempts."
        }
    
    def process_image(self, image_path: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an image (fridge photo or receipt)
        
        Args:
            image_path: Path to image file
            query: Optional query about the image
        
        Returns:
            Processing result
        """
        if query is None:
            query = f"Please analyze this image and extract all ingredients: {image_path}"
        else:
            query = f"{query} Image path: {image_path}"
        
        return self.run(query)
    
    def create_meal_plan(
        self,
        ingredients: List[str],
        dietary_constraints: Optional[List[str]] = None,
        calorie_target: Optional[int] = None,
        meal_count: int = 3
    ) -> Dict[str, Any]:
        """
        Create a complete meal plan
        
        Args:
            ingredients: List of available ingredients
            dietary_constraints: Dietary restrictions
            calorie_target: Target daily calories
            meal_count: Number of meals to plan
        
        Returns:
            Meal plan with nutrition info
        """
        query = f"""
Create a meal plan with these details:
- Available ingredients: {', '.join(ingredients)}
- Dietary constraints: {', '.join(dietary_constraints) if dietary_constraints else 'None'}
- Calorie target: {calorie_target if calorie_target else 'No specific target'}
- Number of meals: {meal_count}

Please:
1. Search for recipes that match these ingredients
2. Calculate nutrition for each recipe
3. Select the best combination of meals
4. Provide a complete meal plan with reasoning
"""
        return self.run(query)
    
    def _enhanced_search_recipes(self, available_ingredients, dietary_constraints=None, max_missing=2, cuisine_type=None):
        """
        Enhanced recipe search that automatically adjusts max_missing based on ingredient count.
        Makes the agent more flexible when user has limited ingredients.
        """
        # Parse ingredients if it's a string
        if isinstance(available_ingredients, str):
            ingredients_list = [i.strip() for i in available_ingredients.split(',') if i.strip()]
        else:
            ingredients_list = available_ingredients
        
        ingredient_count = len(ingredients_list)
        
        # Adjust max_missing based on how many ingredients user has
        if ingredient_count <= 3:
            # Very few ingredients - be very flexible
            adjusted_max_missing = 8
            print(f"🔍 User has only {ingredient_count} ingredients, searching with max_missing={adjusted_max_missing} for flexibility")
        elif ingredient_count <= 5:
            # Few ingredients - be flexible
            adjusted_max_missing = 6
            print(f"🔍 User has {ingredient_count} ingredients, searching with max_missing={adjusted_max_missing}")
        else:
            # Use provided max_missing
            adjusted_max_missing = max_missing
        
        # Call original search function with adjusted parameters
        return self._original_search_recipes(
            available_ingredients=ingredients_list,
            dietary_constraints=dietary_constraints,
            max_missing=adjusted_max_missing,
            cuisine_type=cuisine_type
        )
    
    
    def _update_memory_from_tool(self, tool_name: str, args: Dict, result: Any):
        """Update persistent memory based on tool execution"""
        try:
            if tool_name == 'extract_ingredients_from_image':
                # Vision tool - update fridge inventory
                if isinstance(result, dict) and result.get('success'):
                    ingredients = result.get('ingredients', [])
                    if ingredients:
                        self.memory.update_fridge(ingredients, source='vision')
                        print(f"📦 Added {len(ingredients)} ingredients to fridge")
            
            elif tool_name == 'search_recipes':
                # Recipe search - no automatic memory update
                # User can manually mark favorites/dislikes
                pass
            
            elif tool_name == 'estimate_nutrition':
                # Nutrition estimation - could save meal plan
                if isinstance(result, dict) and result.get('success'):
                    meal_plan = result.get('meal_plan')
                    if meal_plan:
                        self.memory.save_meal_plan(meal_plan)
                        print("💾 Saved meal plan to memory")
        
        except Exception as e:
            print(f"⚠️  Error updating memory: {e}")
    
    
    def get_memory_summary(self) -> str:
        """Get human-readable memory summary"""
        return self.memory.get_summary()
    
    
    def update_fridge_manual(self, ingredients: List[str]) -> Dict:
        """Manually update fridge inventory"""
        return self.memory.update_fridge(ingredients, source='manual')
    
    
    def mark_recipe_as_cooked(self, recipe_name: str, rating: Optional[int] = None) -> Dict:
        """Mark a recipe as cooked"""
        return self.memory.add_cooked_recipe(recipe_name, rating)
    
    
    def add_favorite_recipe(self, recipe_name: str) -> Dict:
        """Add recipe to favorites"""
        return self.memory.add_favorite(recipe_name)
    
    
    def add_disliked_recipe(self, recipe_name: str) -> Dict:
        """Mark recipe as disliked"""
        return self.memory.add_disliked(recipe_name)
    
    
    def set_dietary_preferences(self, constraints: List[str]) -> None:
        """Set dietary constraints"""
        self.memory.set_dietary_constraints(constraints)
        # Refresh system instruction with new preferences
        base_prompt = self._load_system_prompt()
        memory_context = self.memory.get_agent_context()
        self.system_instruction = self._enhance_prompt_with_memory(base_prompt, memory_context)
        print(f"✓ Updated dietary preferences: {', '.join(constraints)}")
    
    
    def set_calorie_target(self, calories: int) -> None:
        """Set daily calorie target"""
        self.memory.set_calorie_target(calories)
        print(f"✓ Set calorie target: {calories}")


def main():
    """Test the ChefByte ADK Agent"""
    print("=== ChefByte ADK Agent Test ===\n")
    
    # Initialize agent
    agent = ChefByteADKAgent()
    
    # Test 1: Simple query
    print("\n--- Test 1: Simple greeting ---")
    result = agent.run("Hello! What can you help me with?")
    if result['success']:
        print(f"Response: {result['response']}")
    else:
        print(f"Error: {result['error']}")
    
    # Test 2: Meal planning query
    print("\n--- Test 2: Meal planning ---")
    result = agent.create_meal_plan(
        ingredients=["tomato", "onion", "rice", "chicken", "spinach"],
        dietary_constraints=["high_protein"],
        calorie_target=1800,
        meal_count=3
    )
    if result['success']:
        print(f"Response: {result['response']}")
    else:
        print(f"Error: {result['error']}")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    main()
