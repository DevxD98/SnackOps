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
    nutrition_estimator_tool
)


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
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ChefByte ADK Agent
        
        Args:
            config_path: Path to config.yaml file
        """
        # Load configuration
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                'config.yaml'
            )
        
        self.config = self._load_config(config_path)
        
        # Load system prompt
        system_prompt = self._load_system_prompt()
        
        # Initialize Gemini client directly
        # Configure API key
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable must be set")
        
        self.client = genai.Client(api_key=api_key)
        
        # Set up model with tools
        self.model_id = self.config['agent']['model']
        self.system_instruction = system_prompt
        
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
        
        # Store function references
        self.tool_functions = {
            'extract_ingredients_from_image': extract_ingredients_from_image,
            'search_recipes': search_recipes,
            'estimate_nutrition': estimate_nutrition
        }
        
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
                        description='Search for recipes matching available ingredients with dietary constraints',
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                'available_ingredients': types.Schema(type=types.Type.STRING, description='Comma-separated list of available ingredients'),
                                'dietary_constraints': types.Schema(type=types.Type.STRING, description='Dietary constraints (e.g., vegetarian, vegan)'),
                                'max_missing': types.Schema(type=types.Type.INTEGER, description='Maximum missing ingredients allowed'),
                                'cuisine_type': types.Schema(type=types.Type.STRING, description='Preferred cuisine type')
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
