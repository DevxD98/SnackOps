"""
Agent Memory Module
Manages the state and history of the ChefByte agent
"""

class AgentMemory:
    """
    Stores the agent's working memory including:
    - Available ingredients
    - Tool execution history
    - Intermediate results
    - Final meal plan
    """
    
    def __init__(self):
        self.ingredients = []
        self.normalized_ingredients = []
        self.recipes = []
        self.tool_history = []
        self.observations = []
        self.meal_plan = None
        self.nutrition_data = {}
        self.dietary_constraints = []
        self.calorie_target = None
        
    def add_ingredients(self, ingredients):
        """Add ingredients to memory"""
        if isinstance(ingredients, list):
            self.ingredients.extend(ingredients)
        else:
            self.ingredients.append(ingredients)
        self.log_observation(f"Added {len(ingredients) if isinstance(ingredients, list) else 1} ingredients")
    
    def set_normalized_ingredients(self, normalized):
        """Store normalized ingredient names"""
        self.normalized_ingredients = normalized
        self.log_observation(f"Normalized {len(normalized)} ingredients")
    
    def add_recipes(self, recipes):
        """Add filtered recipes to memory"""
        self.recipes = recipes
        self.log_observation(f"Found {len(recipes)} matching recipes")
    
    def set_meal_plan(self, meal_plan):
        """Store the final meal plan"""
        self.meal_plan = meal_plan
        self.log_observation("Generated final meal plan")
    
    def set_nutrition_data(self, nutrition_data):
        """Store nutrition calculations"""
        self.nutrition_data = nutrition_data
        self.log_observation("Calculated nutrition information")
    
    def log_tool_use(self, tool_name, input_data, output_data):
        """Log a tool execution"""
        self.tool_history.append({
            'tool': tool_name,
            'input': input_data,
            'output': output_data
        })
    
    def log_observation(self, observation):
        """Add an observation to memory"""
        self.observations.append(observation)
    
    def get_state_summary(self):
        """Get a summary of the current state"""
        return {
            'ingredients_count': len(self.ingredients),
            'normalized_ingredients_count': len(self.normalized_ingredients),
            'recipes_count': len(self.recipes),
            'tools_used': len(self.tool_history),
            'has_meal_plan': self.meal_plan is not None,
            'has_nutrition': bool(self.nutrition_data)
        }
    
    def get_full_context(self):
        """Get complete context for reasoning"""
        return {
            'ingredients': self.ingredients,
            'normalized_ingredients': self.normalized_ingredients,
            'recipes': self.recipes,
            'nutrition_data': self.nutrition_data,
            'dietary_constraints': self.dietary_constraints,
            'calorie_target': self.calorie_target,
            'observations': self.observations,
            'tool_history': [t['tool'] for t in self.tool_history]
        }
    
    def reset(self):
        """Clear all memory"""
        self.__init__()
