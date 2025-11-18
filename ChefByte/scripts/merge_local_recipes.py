"""
Merge local recipe datasets into ChefByte format
Processes:
1. indian_recipes_raw.csv (~50k Indian recipes)
2. better_recipes_raw.csv (~7k Western recipes)
"""
import os
import pandas as pd
import re
from typing import List

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
INDIAN_RECIPES = os.path.join(DATA_DIR, "indian_recipes_raw.csv")
WESTERN_RECIPES = os.path.join(DATA_DIR, "better_recipes_raw.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "recipes.csv")
BACKUP_FILE = os.path.join(DATA_DIR, "recipes_backup.csv")


def clean_ingredients(ingredients_text: str) -> str:
    """Clean and normalize ingredient list"""
    if pd.isna(ingredients_text) or str(ingredients_text).strip() == '':
        return ""
    
    # Convert to string and clean
    ingredients_text = str(ingredients_text).strip()
    
    # Remove measurements and quantities (keep only ingredient names)
    # Split by comma
    if ',' in ingredients_text:
        parts = ingredients_text.split(',')
    else:
        parts = [ingredients_text]
    
    cleaned = []
    for part in parts:
        # Remove numbers, measurements, and parentheses
        part = re.sub(r'\d+(\.\d+)?', '', part)  # Remove numbers
        part = re.sub(r'\(.*?\)', '', part)  # Remove parentheses
        part = re.sub(r'\b(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|pound|pounds|ounce|ounces|gram|grams|kg|lb|oz|tsp|tbsp|ml|liter)\b', '', part, flags=re.IGNORECASE)
        part = part.strip(' -,')
        
        if part and len(part) > 2:  # Only keep meaningful ingredients
            cleaned.append(part.lower())
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for item in cleaned:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    
    return ','.join(unique[:20])  # Limit to 20 ingredients


def clean_instructions(instructions_text: str) -> str:
    """Clean and format cooking instructions"""
    if pd.isna(instructions_text):
        return "No instructions provided."
    
    instructions_text = str(instructions_text).strip()
    instructions_text = re.sub(r'\s+', ' ', instructions_text)  # Remove extra whitespace
    
    # Limit length
    if len(instructions_text) > 800:
        instructions_text = instructions_text[:797] + "..."
    
    return instructions_text


def extract_time(time_text) -> int:
    """Extract numeric time in minutes"""
    if pd.isna(time_text):
        return 30
    
    time_str = str(time_text).strip()
    
    # Try to extract number
    numbers = re.findall(r'\d+', time_str)
    if numbers:
        return min(int(numbers[0]), 300)  # Cap at 5 hours
    
    return 30  # Default


def detect_vegetarian(ingredients: str, name: str = "") -> bool:
    """Detect if recipe is vegetarian"""
    text = (ingredients + " " + name).lower()
    
    meat_keywords = [
        'chicken', 'beef', 'pork', 'lamb', 'mutton', 'fish', 'shrimp', 
        'prawn', 'meat', 'bacon', 'ham', 'turkey', 'duck', 'salmon',
        'tuna', 'crab', 'lobster', 'sausage', 'keema', 'gosht'
    ]
    
    return not any(meat in text for meat in meat_keywords)


def detect_vegan(ingredients: str) -> bool:
    """Detect if recipe is vegan"""
    text = ingredients.lower()
    
    # Check for animal products
    non_vegan = [
        'milk', 'cheese', 'butter', 'ghee', 'yogurt', 'curd', 'egg', 
        'cream', 'paneer', 'honey', 'chicken', 'fish', 'meat'
    ]
    
    return not any(item in text for item in non_vegan)


def detect_gluten_free(ingredients: str) -> bool:
    """Detect if recipe is gluten-free"""
    text = ingredients.lower()
    
    gluten_items = [
        'wheat', 'flour', 'bread', 'pasta', 'noodles', 'roti', 
        'chapati', 'paratha', 'naan', 'maida', 'atta'
    ]
    
    return not any(item in text for item in gluten_items)


def extract_cuisine_tags(cuisine: str, name: str = "") -> str:
    """Extract cuisine and other tags"""
    tags = []
    
    if not pd.isna(cuisine):
        cuisine_lower = str(cuisine).lower()
        tags.append(cuisine_lower.split('/')[0])  # Take first cuisine if multiple
    
    # Add tags from recipe name
    name_lower = name.lower()
    if 'curry' in name_lower:
        tags.append('curry')
    if 'soup' in name_lower:
        tags.append('soup')
    if 'salad' in name_lower:
        tags.append('salad')
    if 'dessert' in name_lower or 'sweet' in name_lower:
        tags.append('dessert')
    if 'quick' in name_lower or 'easy' in name_lower:
        tags.append('quick')
    
    return ','.join(tags[:5]) if tags else 'general'


def process_indian_recipes(file_path: str, max_recipes: int = 10000) -> pd.DataFrame:
    """Process Indian recipes dataset"""
    print(f"\n📥 Loading Indian recipes from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"   Loaded {len(df)} recipes")
        print(f"   Columns: {list(df.columns)}")
        
        # Sample to reduce size (take first max_recipes)
        if len(df) > max_recipes:
            print(f"   Sampling {max_recipes} recipes...")
            df = df.head(max_recipes)
        
        # Transform to ChefByte format
        chefbyte_df = pd.DataFrame()
        
        chefbyte_df['name'] = df['TranslatedRecipeName']
        chefbyte_df['ingredients'] = df['TranslatedIngredients'].apply(clean_ingredients)
        chefbyte_df['instructions'] = df['TranslatedInstructions'].apply(clean_instructions)
        chefbyte_df['prep_time'] = 15  # Default since not provided
        chefbyte_df['cook_time'] = df['TotalTimeInMins'].apply(extract_time)
        chefbyte_df['servings'] = 4  # Default
        chefbyte_df['tags'] = df.apply(lambda row: extract_cuisine_tags(row['Cuisine'], row['TranslatedRecipeName']), axis=1)
        chefbyte_df['vegetarian'] = df.apply(lambda row: detect_vegetarian(str(row['TranslatedIngredients']), str(row['TranslatedRecipeName'])), axis=1)
        chefbyte_df['vegan'] = df['TranslatedIngredients'].apply(detect_vegan)
        chefbyte_df['gluten-free'] = df['TranslatedIngredients'].apply(detect_gluten_free)
        
        # Remove rows with empty ingredients
        chefbyte_df = chefbyte_df[chefbyte_df['ingredients'].str.len() > 0]
        
        print(f"   ✓ Processed {len(chefbyte_df)} Indian recipes")
        return chefbyte_df
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return pd.DataFrame()


def process_western_recipes(file_path: str, max_recipes: int = 5000) -> pd.DataFrame:
    """Process Western recipes dataset"""
    print(f"\n📥 Loading Western recipes from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        print(f"   Loaded {len(df)} recipes")
        print(f"   Columns: {list(df.columns)}")
        
        # Sample to reduce size
        if len(df) > max_recipes:
            print(f"   Sampling {max_recipes} recipes...")
            df = df.head(max_recipes)
        
        # Transform to ChefByte format
        chefbyte_df = pd.DataFrame()
        
        chefbyte_df['name'] = df['recipe_name']
        chefbyte_df['ingredients'] = df['ingredients'].apply(clean_ingredients)
        chefbyte_df['instructions'] = df['directions'].apply(clean_instructions)
        chefbyte_df['prep_time'] = df['prep_time'].apply(extract_time)
        chefbyte_df['cook_time'] = df['cook_time'].apply(extract_time)
        chefbyte_df['servings'] = df['servings'].apply(lambda x: int(x) if not pd.isna(x) and str(x).isdigit() else 4)
        chefbyte_df['tags'] = df.apply(lambda row: extract_cuisine_tags(row.get('cuisine_path', ''), str(row['recipe_name'])), axis=1)
        chefbyte_df['vegetarian'] = df.apply(lambda row: detect_vegetarian(str(row['ingredients']), str(row['recipe_name'])), axis=1)
        chefbyte_df['vegan'] = df['ingredients'].apply(detect_vegan)
        chefbyte_df['gluten-free'] = df['ingredients'].apply(detect_gluten_free)
        
        # Remove rows with empty ingredients
        chefbyte_df = chefbyte_df[chefbyte_df['ingredients'].str.len() > 0]
        
        print(f"   ✓ Processed {len(chefbyte_df)} Western recipes")
        return chefbyte_df
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return pd.DataFrame()


def main():
    print("🔥 ChefByte Recipe Merger")
    print("=" * 60)
    
    all_recipes = []
    
    # Process Indian recipes (take 10k)
    if os.path.exists(INDIAN_RECIPES):
        indian_df = process_indian_recipes(INDIAN_RECIPES, max_recipes=10000)
        if not indian_df.empty:
            all_recipes.append(indian_df)
    else:
        print(f"⚠️  Indian recipes file not found: {INDIAN_RECIPES}")
    
    # Process Western recipes (take 5k)
    if os.path.exists(WESTERN_RECIPES):
        western_df = process_western_recipes(WESTERN_RECIPES, max_recipes=5000)
        if not western_df.empty:
            all_recipes.append(western_df)
    else:
        print(f"⚠️  Western recipes file not found: {WESTERN_RECIPES}")
    
    if not all_recipes:
        print("\n❌ No recipes to merge!")
        return
    
    # Merge all datasets
    print("\n🔗 Merging datasets...")
    merged_df = pd.concat(all_recipes, ignore_index=True)
    print(f"   Total recipes before deduplication: {len(merged_df)}")
    
    # Remove duplicates
    merged_df = merged_df.drop_duplicates(subset=['name'], keep='first')
    print(f"   Total recipes after deduplication: {len(merged_df)}")
    
    # Backup existing recipes
    if os.path.exists(OUTPUT_FILE):
        print(f"\n💾 Backing up existing recipes to: {BACKUP_FILE}")
        import shutil
        shutil.copy(OUTPUT_FILE, BACKUP_FILE)
    
    # Save merged dataset
    print(f"\n💾 Saving {len(merged_df)} recipes to: {OUTPUT_FILE}")
    merged_df.to_csv(OUTPUT_FILE, index=False)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 MERGE SUMMARY")
    print("=" * 60)
    print(f"Total Recipes: {len(merged_df)}")
    print(f"Vegetarian: {merged_df['vegetarian'].sum()} ({merged_df['vegetarian'].sum()/len(merged_df)*100:.1f}%)")
    print(f"Vegan: {merged_df['vegan'].sum()} ({merged_df['vegan'].sum()/len(merged_df)*100:.1f}%)")
    print(f"Gluten-Free: {merged_df['gluten-free'].sum()} ({merged_df['gluten-free'].sum()/len(merged_df)*100:.1f}%)")
    print(f"\nAverage Prep Time: {merged_df['prep_time'].mean():.1f} min")
    print(f"Average Cook Time: {merged_df['cook_time'].mean():.1f} min")
    print(f"Average Servings: {merged_df['servings'].mean():.1f}")
    
    # Top cuisines
    print("\n🍛 Top Cuisine Tags:")
    tags_series = merged_df['tags'].str.split(',').explode()
    print(tags_series.value_counts().head(10).to_string())
    
    # Sample recipes
    print("\n📋 Sample Recipes:")
    print(merged_df[['name', 'tags', 'vegetarian', 'cook_time']].head(15).to_string(index=False))
    
    print("\n✅ Recipe merge complete!")
    print(f"   Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
