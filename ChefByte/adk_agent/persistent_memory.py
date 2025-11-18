"""
Persistent Memory System for ChefByte Agent
Tracks fridge inventory, recipe history, and user preferences across sessions
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class PersistentMemory:
    """
    Manages persistent storage of:
    - Fridge inventory (ingredients detected from images)
    - Recipe history (previously made recipes)
    - User preferences (dietary restrictions, favorites, dislikes)
    - Meal planning history
    """
    
    def __init__(self, user_id: str = "default_user", storage_dir: str = None):
        """
        Initialize persistent memory for a user
        
        Args:
            user_id: Unique identifier for the user
            storage_dir: Directory to store memory files (default: data/memory/)
        """
        self.user_id = user_id
        
        # Set storage directory
        if storage_dir is None:
            storage_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "memory"
            )
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # User-specific file paths
        self.fridge_file = self.storage_dir / f"{user_id}_fridge.json"
        self.history_file = self.storage_dir / f"{user_id}_history.json"
        self.preferences_file = self.storage_dir / f"{user_id}_preferences.json"
        
        # Load existing data
        self.fridge_inventory = self._load_json(self.fridge_file, default={
            "ingredients": [],
            "last_updated": None,
            "scan_history": []
        })
        
        self.recipe_history = self._load_json(self.history_file, default={
            "cooked_recipes": [],
            "favorite_recipes": [],
            "disliked_recipes": [],
            "meal_plans": []
        })
        
        self.user_preferences = self._load_json(self.preferences_file, default={
            "dietary_constraints": [],
            "cuisine_preferences": [],
            "calorie_target": None,
            "allergies": [],
            "default_servings": 4
        })
    
    
    def _load_json(self, file_path: Path, default: Dict) -> Dict:
        """Load JSON file or return default if not exists"""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading {file_path}: {e}")
                return default
        return default
    
    
    def _save_json(self, file_path: Path, data: Dict):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving {file_path}: {e}")
    
    
    # ==================== FRIDGE INVENTORY ====================
    
    def update_fridge(self, ingredients: List[str], source: str = "manual"):
        """
        Update fridge inventory with new ingredients
        
        Args:
            ingredients: List of ingredient names
            source: How ingredients were added ('vision', 'manual', 'voice')
        """
        # Normalize ingredients (lowercase, strip)
        normalized = [ing.lower().strip() for ing in ingredients]
        
        # Add to existing inventory (avoid duplicates)
        current = set(self.fridge_inventory["ingredients"])
        current.update(normalized)
        
        self.fridge_inventory["ingredients"] = sorted(list(current))
        self.fridge_inventory["last_updated"] = datetime.now().isoformat()
        
        # Log scan history
        self.fridge_inventory["scan_history"].append({
            "timestamp": datetime.now().isoformat(),
            "ingredients": normalized,
            "source": source,
            "count": len(normalized)
        })
        
        # Keep only last 50 scans
        self.fridge_inventory["scan_history"] = self.fridge_inventory["scan_history"][-50:]
        
        self._save_json(self.fridge_file, self.fridge_inventory)
        
        return {
            "success": True,
            "total_ingredients": len(self.fridge_inventory["ingredients"]),
            "new_ingredients": len(normalized)
        }
    
    
    def remove_ingredients(self, ingredients: List[str]):
        """Remove ingredients from fridge (e.g., after cooking)"""
        normalized = [ing.lower().strip() for ing in ingredients]
        current = set(self.fridge_inventory["ingredients"])
        
        current.difference_update(normalized)
        
        self.fridge_inventory["ingredients"] = sorted(list(current))
        self.fridge_inventory["last_updated"] = datetime.now().isoformat()
        
        self._save_json(self.fridge_file, self.fridge_inventory)
        
        return {
            "success": True,
            "removed_count": len(normalized),
            "remaining_count": len(self.fridge_inventory["ingredients"])
        }
    
    
    def get_fridge_inventory(self) -> List[str]:
        """Get current fridge inventory"""
        return self.fridge_inventory["ingredients"]
    
    
    def clear_fridge(self):
        """Clear all ingredients from fridge"""
        self.fridge_inventory["ingredients"] = []
        self.fridge_inventory["last_updated"] = datetime.now().isoformat()
        self._save_json(self.fridge_file, self.fridge_inventory)
    
    
    # ==================== RECIPE HISTORY ====================
    
    def add_cooked_recipe(self, recipe_name: str, rating: Optional[int] = None, notes: str = ""):
        """
        Record that a recipe was cooked
        
        Args:
            recipe_name: Name of the recipe
            rating: Optional rating (1-5)
            notes: Optional cooking notes
        """
        entry = {
            "recipe_name": recipe_name,
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "notes": notes
        }
        
        self.recipe_history["cooked_recipes"].append(entry)
        
        # Keep only last 100 cooked recipes
        self.recipe_history["cooked_recipes"] = self.recipe_history["cooked_recipes"][-100:]
        
        self._save_json(self.history_file, self.recipe_history)
        
        return {"success": True, "total_cooked": len(self.recipe_history["cooked_recipes"])}
    
    
    def add_favorite(self, recipe_name: str):
        """Add recipe to favorites"""
        if recipe_name not in self.recipe_history["favorite_recipes"]:
            self.recipe_history["favorite_recipes"].append(recipe_name)
            self._save_json(self.history_file, self.recipe_history)
            return {"success": True, "message": f"Added {recipe_name} to favorites"}
        return {"success": False, "message": "Already in favorites"}
    
    
    def remove_favorite(self, recipe_name: str):
        """Remove recipe from favorites"""
        if recipe_name in self.recipe_history["favorite_recipes"]:
            self.recipe_history["favorite_recipes"].remove(recipe_name)
            self._save_json(self.history_file, self.recipe_history)
            return {"success": True, "message": f"Removed {recipe_name} from favorites"}
        return {"success": False, "message": "Not in favorites"}
    
    
    def add_disliked(self, recipe_name: str):
        """Mark recipe as disliked (won't be suggested)"""
        if recipe_name not in self.recipe_history["disliked_recipes"]:
            self.recipe_history["disliked_recipes"].append(recipe_name)
            self._save_json(self.history_file, self.recipe_history)
            return {"success": True, "message": f"Marked {recipe_name} as disliked"}
        return {"success": False, "message": "Already marked as disliked"}
    
    
    def get_recipe_history(self, limit: int = 10) -> List[Dict]:
        """Get recently cooked recipes"""
        return self.recipe_history["cooked_recipes"][-limit:]
    
    
    def get_favorites(self) -> List[str]:
        """Get favorite recipes"""
        return self.recipe_history["favorite_recipes"]
    
    
    def get_disliked(self) -> List[str]:
        """Get disliked recipes (to filter out)"""
        return self.recipe_history["disliked_recipes"]
    
    
    def save_meal_plan(self, meal_plan: Dict):
        """Save a generated meal plan"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "plan": meal_plan
        }
        
        self.recipe_history["meal_plans"].append(entry)
        
        # Keep only last 20 meal plans
        self.recipe_history["meal_plans"] = self.recipe_history["meal_plans"][-20:]
        
        self._save_json(self.history_file, self.recipe_history)
    
    
    # ==================== USER PREFERENCES ====================
    
    def set_dietary_constraints(self, constraints: List[str]):
        """Set dietary constraints (vegetarian, vegan, gluten-free, etc.)"""
        self.user_preferences["dietary_constraints"] = constraints
        self._save_json(self.preferences_file, self.user_preferences)
    
    
    def add_dietary_constraint(self, constraint: str):
        """Add a dietary constraint"""
        if constraint not in self.user_preferences["dietary_constraints"]:
            self.user_preferences["dietary_constraints"].append(constraint)
            self._save_json(self.preferences_file, self.user_preferences)
    
    
    def set_cuisine_preferences(self, cuisines: List[str]):
        """Set preferred cuisines"""
        self.user_preferences["cuisine_preferences"] = cuisines
        self._save_json(self.preferences_file, self.user_preferences)
    
    
    def set_calorie_target(self, calories: int):
        """Set daily calorie target"""
        self.user_preferences["calorie_target"] = calories
        self._save_json(self.preferences_file, self.user_preferences)
    
    
    def set_allergies(self, allergies: List[str]):
        """Set food allergies"""
        self.user_preferences["allergies"] = allergies
        self._save_json(self.preferences_file, self.user_preferences)
    
    
    def get_preferences(self) -> Dict:
        """Get all user preferences"""
        return self.user_preferences
    
    
    # ==================== CONTEXT FOR AGENT ====================
    
    def get_agent_context(self) -> Dict[str, Any]:
        """
        Get complete context for agent to use in decision making
        
        Returns:
            Dictionary with fridge inventory, preferences, and history
        """
        return {
            "fridge_inventory": self.fridge_inventory["ingredients"],
            "fridge_last_updated": self.fridge_inventory["last_updated"],
            "total_ingredients": len(self.fridge_inventory["ingredients"]),
            
            "dietary_constraints": self.user_preferences["dietary_constraints"],
            "cuisine_preferences": self.user_preferences["cuisine_preferences"],
            "calorie_target": self.user_preferences["calorie_target"],
            "allergies": self.user_preferences["allergies"],
            
            "recent_recipes": [r["recipe_name"] for r in self.recipe_history["cooked_recipes"][-5:]],
            "favorite_recipes": self.recipe_history["favorite_recipes"],
            "disliked_recipes": self.recipe_history["disliked_recipes"],
            
            "total_cooked": len(self.recipe_history["cooked_recipes"]),
            "total_favorites": len(self.recipe_history["favorite_recipes"])
        }
    
    
    def get_summary(self) -> str:
        """Get human-readable summary of memory state"""
        ctx = self.get_agent_context()
        
        summary = f"""
📦 **Fridge Inventory**: {ctx['total_ingredients']} ingredients
   {', '.join(ctx['fridge_inventory'][:10])}{'...' if len(ctx['fridge_inventory']) > 10 else ''}

🍽️ **Cooking History**: {ctx['total_cooked']} recipes cooked
   Recent: {', '.join(ctx['recent_recipes']) if ctx['recent_recipes'] else 'None'}

⭐ **Favorites**: {ctx['total_favorites']} recipes
   {', '.join(ctx['favorite_recipes'][:5])}{'...' if len(ctx['favorite_recipes']) > 5 else ''}

🥗 **Dietary Preferences**: {', '.join(ctx['dietary_constraints']) if ctx['dietary_constraints'] else 'None set'}

🎯 **Calorie Target**: {ctx['calorie_target'] if ctx['calorie_target'] else 'Not set'}
"""
        return summary.strip()
