"""
PantryPilot Agent Orchestrator
Main agent that coordinates all tools using Reason → Act → Observe pattern
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gemini_setup import get_gemini_model
from agent.memory import AgentMemory
from agent.tools.vision_tool import extract_ingredients_from_image
from agent.tools.receipt_ocr_tool import extract_items_from_receipt
from agent.tools.ingredient_normalizer import normalize_ingredients
from agent.tools.recipe_search import search_recipes
from agent.tools.nutrition_estimator import calculate_nutrition


class PantryPilotAgent:
    """
    Main orchestrator for the PantryPilot AI agent
    Uses Gemini Pro to reason about which tools to use and when
    """
    
    def __init__(self):
        self.model = get_gemini_model("gemini-pro")
        self.memory = AgentMemory()
        self.max_iterations = 10
        
        # Available tools
        self.tools = {
            'vision_tool': extract_ingredients_from_image,
            'receipt_ocr': extract_items_from_receipt,
            'normalizer': normalize_ingredients,
            'recipe_search': search_recipes,
            'nutrition_calc': calculate_nutrition
        }
    
    def run(self, fridge_image=None, receipt_image=None, 
            dietary_constraints=None, calorie_target=None, meal_count=3):
        """
        Main entry point for the agent
        
        Args:
            fridge_image: Path to fridge photo
            receipt_image: Path to receipt image (optional)
            dietary_constraints: List of dietary requirements (e.g., ['vegetarian', 'gluten-free'])
            calorie_target: Target calories per day
            meal_count: Number of meals to plan
        
        Returns:
            Dictionary with meal plan and reasoning
        """
        # Initialize memory with constraints
        self.memory.dietary_constraints = dietary_constraints or []
        self.memory.calorie_target = calorie_target
        
        # Step 1: Extract ingredients from fridge
        if fridge_image:
            print("🔍 Analyzing fridge image...")
            ingredients = self.tools['vision_tool'](fridge_image)
            self.memory.add_ingredients(ingredients)
            self.memory.log_tool_use('vision_tool', fridge_image, ingredients)
        
        # Step 2: Extract items from receipt (optional)
        if receipt_image:
            print("📄 Processing receipt...")
            receipt_items = self.tools['receipt_ocr'](receipt_image)
            self.memory.add_ingredients(receipt_items)
            self.memory.log_tool_use('receipt_ocr', receipt_image, receipt_items)
        
        # Step 3: Normalize ingredients
        if self.memory.ingredients:
            print("🔤 Normalizing ingredient names...")
            normalized = self.tools['normalizer'](self.memory.ingredients)
            self.memory.set_normalized_ingredients(normalized)
            self.memory.log_tool_use('normalizer', self.memory.ingredients, normalized)
        
        # Step 4: Search for recipes
        print("🔍 Searching for matching recipes...")
        recipes = self.tools['recipe_search'](
            self.memory.normalized_ingredients,
            dietary_constraints=self.memory.dietary_constraints
        )
        self.memory.add_recipes(recipes)
        self.memory.log_tool_use('recipe_search', 
                                  {'ingredients': self.memory.normalized_ingredients,
                                   'constraints': dietary_constraints}, 
                                  recipes)
        
        # Step 5: Calculate nutrition and select best meals
        print("📊 Calculating nutrition and selecting meals...")
        nutrition_data = self.tools['nutrition_calc'](
            recipes,
            calorie_target=calorie_target,
            meal_count=meal_count
        )
        self.memory.set_nutrition_data(nutrition_data)
        self.memory.log_tool_use('nutrition_calc', 
                                  {'recipes': len(recipes), 'target': calorie_target},
                                  nutrition_data)
        
        # Step 6: Generate final meal plan with reasoning
        print("🤖 Generating meal plan with reasoning...")
        meal_plan = self._generate_final_plan(meal_count)
        self.memory.set_meal_plan(meal_plan)
        
        return meal_plan
    
    def _generate_final_plan(self, meal_count):
        """
        Use Gemini to generate a coherent meal plan with reasoning
        """
        context = self.memory.get_full_context()
        
        prompt = f"""
You are PantryPilot, an AI meal planning assistant. Based on the following information, 
create a detailed meal plan with reasoning.

AVAILABLE INGREDIENTS:
{', '.join(context['normalized_ingredients'])}

DIETARY CONSTRAINTS:
{', '.join(context['dietary_constraints']) if context['dietary_constraints'] else 'None'}

CALORIE TARGET:
{context['calorie_target'] if context['calorie_target'] else 'Not specified'}

AVAILABLE RECIPES:
{self._format_recipes_for_prompt()}

NUTRITION DATA:
{context['nutrition_data']}

TASK:
Create a meal plan with {meal_count} meals. For each meal:
1. Select the best recipe based on ingredients, nutrition, and constraints
2. Explain WHY this recipe was chosen
3. List ingredients needed
4. Provide nutrition breakdown

Also provide:
- Overall reasoning for the meal plan
- Total nutrition summary
- Any ingredients that weren't used
- Suggestions for improvement

Format your response as a structured meal plan.
        """
        
        response = self.model.generate_content(prompt)
        
        return {
            'meal_plan': response.text,
            'reasoning': self._extract_reasoning(response.text),
            'ingredients_used': context['normalized_ingredients'],
            'recipes_considered': len(context['recipes']),
            'nutrition_summary': context['nutrition_data'],
            'tool_history': context['tool_history']
        }
    
    def _format_recipes_for_prompt(self):
        """Format recipes for the prompt"""
        recipes = self.memory.recipes
        if not recipes:
            return "No recipes found"
        
        formatted = []
        for i, recipe in enumerate(recipes[:10], 1):  # Limit to top 10
            formatted.append(f"{i}. {recipe.get('name', 'Unknown')} - "
                           f"Ingredients: {recipe.get('ingredients', 'N/A')}")
        
        return '\n'.join(formatted)
    
    def _extract_reasoning(self, text):
        """Extract reasoning section from response"""
        # Simple extraction - in production, use more sophisticated parsing
        if "REASONING:" in text.upper():
            parts = text.split("REASONING:")
            if len(parts) > 1:
                return parts[1].split("\n\n")[0].strip()
        return "See full meal plan for detailed reasoning"
    
    def get_memory_state(self):
        """Get current memory state for debugging"""
        return self.memory.get_state_summary()
    
    def reset(self):
        """Reset the agent"""
        self.memory.reset()


def main():
    """Example usage"""
    agent = PantryPilotAgent()
    
    # Example run
    result = agent.run(
        fridge_image="path/to/fridge.jpg",
        dietary_constraints=["vegetarian"],
        calorie_target=2000,
        meal_count=3
    )
    
    print("\n" + "="*50)
    print("MEAL PLAN GENERATED")
    print("="*50)
    print(result['meal_plan'])
    print("\n" + "="*50)
    print(f"Recipes considered: {result['recipes_considered']}")
    print(f"Tools used: {', '.join(result['tool_history'])}")


if __name__ == "__main__":
    main()
