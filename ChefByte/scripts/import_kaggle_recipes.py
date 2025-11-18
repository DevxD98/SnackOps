"""
Import and merge Kaggle recipe datasets into ChefByte format
Downloads 2 datasets:
1. Indian Recipes (sooryaprakash12/cleaned-indian-recipes-dataset)
2. Better Recipes (thedevastator/better-recipes-for-a-better-life)
"""
import os
import sys
import pandas as pd
import kagglehub
from kagglehub import KaggleDatasetAdapter
import re
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_ingredients(ingredients_text: str) -> str:
    """Clean and normalize ingredient list"""
    if pd.isna(ingredients_text):
        return ""
    
    # Remove extra whitespace, newlines, and special characters
    ingredients_text = str(ingredients_text).strip()
    ingredients_text = re.sub(r'\s+', ' ', ingredients_text)
    ingredients_text = re.sub(r'[\[\]"\']', '', ingredients_text)
    
    # Split by common separators
    if ',' in ingredients_text:
        ingredients = [i.strip().lower() for i in ingredients_text.split(',')]
    elif '\n' in ingredients_text:
        ingredients = [i.strip().lower() for i in ingredients_text.split('\n')]
    else:
        ingredients = [ingredients_text.lower()]
    
    # Remove empty entries
    ingredients = [i for i in ingredients if i and len(i) > 0]
    
    return ','.join(ingredients[:20])  # Limit to 20 ingredients


def clean_instructions(instructions_text: str) -> str:
    """Clean and format cooking instructions"""
    if pd.isna(instructions_text):
        return "No instructions provided."
    
    instructions_text = str(instructions_text).strip()
    instructions_text = re.sub(r'\s+', ' ', instructions_text)
    
    # Limit length to avoid token issues
    if len(instructions_text) > 500:
        instructions_text = instructions_text[:497] + "..."
    
    return instructions_text


def extract_tags(row: pd.Series) -> str:
    """Extract tags from recipe data"""
    tags = []
    
    # Check for cuisine type
    if 'cuisine' in row and not pd.isna(row['cuisine']):
        tags.append(str(row['cuisine']).lower())
    if 'course' in row and not pd.isna(row['course']):
        tags.append(str(row['course']).lower())
    if 'diet' in row and not pd.isna(row['diet']):
        tags.append(str(row['diet']).lower())
    
    # Time-based tags
    if 'prep_time' in row:
        try:
            prep_time = int(row['prep_time']) if not pd.isna(row['prep_time']) else 0
            if prep_time <= 15:
                tags.append('quick')
        except:
            pass
    
    return ','.join(tags[:10]) if tags else 'general'


def is_vegetarian(row: pd.Series) -> bool:
    """Determine if recipe is vegetarian"""
    # Check diet column
    if 'diet' in row and not pd.isna(row['diet']):
        diet = str(row['diet']).lower()
        if 'vegetarian' in diet or 'vegan' in diet:
            return True
    
    # Check ingredients for meat
    if 'ingredients' in row and not pd.isna(row['ingredients']):
        ingredients = str(row['ingredients']).lower()
        meat_keywords = ['chicken', 'beef', 'pork', 'lamb', 'fish', 'shrimp', 'meat', 'mutton']
        if any(meat in ingredients for meat in meat_keywords):
            return False
    
    return True  # Default to True for Indian recipes


def is_vegan(row: pd.Series) -> bool:
    """Determine if recipe is vegan"""
    if 'diet' in row and not pd.isna(row['diet']):
        diet = str(row['diet']).lower()
        if 'vegan' in diet:
            return True
    
    if 'ingredients' in row and not pd.isna(row['ingredients']):
        ingredients = str(row['ingredients']).lower()
        non_vegan = ['milk', 'cheese', 'butter', 'ghee', 'yogurt', 'egg', 'cream', 'paneer']
        if any(item in ingredients for item in non_vegan):
            return False
    
    return False


def is_gluten_free(row: pd.Series) -> bool:
    """Determine if recipe is gluten-free"""
    if 'ingredients' in row and not pd.isna(row['ingredients']):
        ingredients = str(row['ingredients']).lower()
        gluten_items = ['wheat', 'flour', 'bread', 'pasta', 'noodles', 'roti', 'chapati']
        if any(item in ingredients for item in gluten_items):
            return False
    
    return True


def transform_to_chefbyte_format(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    """Transform Kaggle dataset to ChefByte format"""
    print(f"\n📊 Processing {dataset_name}...")
    print(f"   Original columns: {list(df.columns)}")
    print(f"   Original rows: {len(df)}")
    
    # Create new dataframe with ChefByte schema
    chefbyte_df = pd.DataFrame()
    
    # Map name field
    if 'name' in df.columns:
        chefbyte_df['name'] = df['name']
    elif 'title' in df.columns:
        chefbyte_df['name'] = df['title']
    elif 'recipe_name' in df.columns:
        chefbyte_df['name'] = df['recipe_name']
    else:
        print(f"   ⚠️  No name column found!")
        return pd.DataFrame()
    
    # Map ingredients
    if 'ingredients' in df.columns:
        chefbyte_df['ingredients'] = df['ingredients'].apply(clean_ingredients)
    elif 'ingredient_list' in df.columns:
        chefbyte_df['ingredients'] = df['ingredient_list'].apply(clean_ingredients)
    else:
        print(f"   ⚠️  No ingredients column found!")
        return pd.DataFrame()
    
    # Map instructions
    if 'instructions' in df.columns:
        chefbyte_df['instructions'] = df['instructions'].apply(clean_instructions)
    elif 'directions' in df.columns:
        chefbyte_df['instructions'] = df['directions'].apply(clean_instructions)
    elif 'method' in df.columns:
        chefbyte_df['instructions'] = df['method'].apply(clean_instructions)
    else:
        chefbyte_df['instructions'] = "Follow standard cooking procedure."
    
    # Map timing
    if 'prep_time' in df.columns:
        chefbyte_df['prep_time'] = pd.to_numeric(df['prep_time'], errors='coerce').fillna(15).astype(int)
    elif 'prep_time_minutes' in df.columns:
        chefbyte_df['prep_time'] = pd.to_numeric(df['prep_time_minutes'], errors='coerce').fillna(15).astype(int)
    else:
        chefbyte_df['prep_time'] = 15
    
    if 'cook_time' in df.columns:
        chefbyte_df['cook_time'] = pd.to_numeric(df['cook_time'], errors='coerce').fillna(30).astype(int)
    elif 'cook_time_minutes' in df.columns:
        chefbyte_df['cook_time'] = pd.to_numeric(df['cook_time_minutes'], errors='coerce').fillna(30).astype(int)
    else:
        chefbyte_df['cook_time'] = 30
    
    # Map servings
    if 'servings' in df.columns:
        chefbyte_df['servings'] = pd.to_numeric(df['servings'], errors='coerce').fillna(4).astype(int)
    else:
        chefbyte_df['servings'] = 4
    
    # Extract tags
    chefbyte_df['tags'] = df.apply(extract_tags, axis=1)
    
    # Dietary flags
    chefbyte_df['vegetarian'] = df.apply(is_vegetarian, axis=1)
    chefbyte_df['vegan'] = df.apply(is_vegan, axis=1)
    chefbyte_df['gluten-free'] = df.apply(is_gluten_free, axis=1)
    
    # Remove rows with missing critical data
    chefbyte_df = chefbyte_df[
        (chefbyte_df['name'].notna()) & 
        (chefbyte_df['ingredients'].str.len() > 0)
    ]
    
    print(f"   ✓ Processed rows: {len(chefbyte_df)}")
    return chefbyte_df


def main():
    print("🔥 ChefByte Recipe Importer")
    print("=" * 50)
    
    all_recipes = []
    
    # Dataset 1: Indian Recipes
    try:
        print("\n📥 Downloading Indian Recipes Dataset...")
        df1 = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "sooryaprakash12/cleaned-indian-recipes-dataset",
            ""
        )
        print(f"✓ Downloaded: {len(df1)} records")
        
        df1_transformed = transform_to_chefbyte_format(df1, "Indian Recipes")
        if not df1_transformed.empty:
            all_recipes.append(df1_transformed)
    except Exception as e:
        print(f"❌ Error loading Indian recipes: {e}")
    
    # Dataset 2: Better Recipes
    try:
        print("\n📥 Downloading Better Recipes Dataset...")
        df2 = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "thedevastator/better-recipes-for-a-better-life",
            ""
        )
        print(f"✓ Downloaded: {len(df2)} records")
        
        df2_transformed = transform_to_chefbyte_format(df2, "Better Recipes")
        if not df2_transformed.empty:
            all_recipes.append(df2_transformed)
    except Exception as e:
        print(f"❌ Error loading better recipes: {e}")
    
    # Merge all datasets
    if not all_recipes:
        print("\n❌ No recipes loaded successfully!")
        return
    
    print("\n🔗 Merging datasets...")
    merged_df = pd.concat(all_recipes, ignore_index=True)
    
    # Remove duplicates based on name
    print(f"   Total before deduplication: {len(merged_df)}")
    merged_df = merged_df.drop_duplicates(subset=['name'], keep='first')
    print(f"   Total after deduplication: {len(merged_df)}")
    
    # Load existing recipes
    recipes_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "recipes.csv"
    )
    
    backup_path = recipes_path.replace('.csv', '_backup.csv')
    
    # Backup existing file
    if os.path.exists(recipes_path):
        print(f"\n💾 Backing up existing recipes to: {backup_path}")
        existing_df = pd.read_csv(recipes_path)
        existing_df.to_csv(backup_path, index=False)
        print(f"   Existing recipes: {len(existing_df)}")
        
        # Optionally merge with existing
        print("\n🔀 Merging with existing recipes...")
        merged_df = pd.concat([existing_df, merged_df], ignore_index=True)
        merged_df = merged_df.drop_duplicates(subset=['name'], keep='first')
    
    # Save merged dataset
    print(f"\n💾 Saving {len(merged_df)} recipes to: {recipes_path}")
    merged_df.to_csv(recipes_path, index=False)
    
    # Print statistics
    print("\n" + "=" * 50)
    print("📊 IMPORT SUMMARY")
    print("=" * 50)
    print(f"Total Recipes: {len(merged_df)}")
    print(f"Vegetarian: {merged_df['vegetarian'].sum()}")
    print(f"Vegan: {merged_df['vegan'].sum()}")
    print(f"Gluten-Free: {merged_df['gluten-free'].sum()}")
    print(f"\nAverage Prep Time: {merged_df['prep_time'].mean():.1f} min")
    print(f"Average Cook Time: {merged_df['cook_time'].mean():.1f} min")
    print(f"Average Servings: {merged_df['servings'].mean():.1f}")
    
    # Sample recipes
    print("\n📋 Sample Recipes:")
    print(merged_df[['name', 'tags', 'vegetarian']].head(10).to_string())
    
    print("\n✅ Recipe import complete!")


if __name__ == "__main__":
    main()
