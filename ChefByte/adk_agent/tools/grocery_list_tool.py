from google.ai.generativelanguage_v1beta.types import FunctionDeclaration, Tool, Schema, Type
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_grocery_list(items: List[str], meal_plan_context: Optional[str] = None) -> Dict:
    """
    Generates a structured grocery list from a list of items or a meal plan context.
    Organizes items by category (Produce, Dairy, Pantry, etc.).
    """
    logger.info(f"Generating grocery list for {len(items)} items")
    
    # In a real implementation, this might use an LLM or a database to categorize items.
    # For this hackathon/demo, we will use a simple keyword-based categorization.
    
    categories = {
        "Produce": ["tomato", "onion", "potato", "spinach", "cilantro", "ginger", "garlic", "chilli", "lemon", "vegetable", "fruit"],
        "Dairy": ["milk", "curd", "yogurt", "paneer", "cheese", "butter", "ghee", "cream"],
        "Grains & Spices": ["rice", "flour", "atta", "dal", "lentil", "spice", "masala", "cumin", "turmeric", "salt", "sugar"],
        "Meat": ["chicken", "mutton", "fish", "egg", "meat"],
        "Bakery": ["bread", "bun"],
        "Other": []
    }
    
    grocery_list = {cat: [] for cat in categories}
    
    for item in items:
        item_lower = item.lower()
        placed = False
        for cat, keywords in categories.items():
            if any(k in item_lower for k in keywords):
                grocery_list[cat].append(item)
                placed = True
                break
        if not placed:
            grocery_list["Other"].append(item)
            
    # Remove empty categories
    grocery_list = {k: v for k, v in grocery_list.items() if v}
    
    return {
        "grocery_list": grocery_list,
        "total_items": len(items),
        "context": meal_plan_context or "Manual List"
    }

# ADK Tool Definition
grocery_list_tool_def = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="generate_grocery_list",
            description="Generates a categorized grocery list from a list of ingredients or items.",
            parameters=Schema(
                type=Type.OBJECT,
                properties={
                    "items": Schema(
                        type=Type.ARRAY,
                        items=Schema(type=Type.STRING),
                        description="List of ingredients or items to add to the grocery list."
                    ),
                    "meal_plan_context": Schema(
                        type=Type.STRING,
                        description="Optional context about the meal plan this list is for."
                    )
                },
                required=["items"]
            )
        )
    ]
)
