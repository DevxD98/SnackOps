/**
 * API Service for Chefbyte-UI
 * Connects to ChefByte FastAPI backend instead of direct Gemini API
 * This gives us access to:
 * - 6,889 recipe database
 * - 9,318 ingredient nutrition database with precise calculations
 * - Fuzzy ingredient matching
 * - User memory and preferences
 */

import { UserPreferences, ChefResponse } from "../types";

// Backend API base URL
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * Generate meal plan from fridge/receipt image or text input
 */
export const generateMealPlan = async (
  inputMode: 'image' | 'text',
  data: string,
  prefs: UserPreferences,
  excludeRecipeTitles: string[] = [],
  currentInventory: string[] = []
): Promise<ChefResponse> => {
  
  try {
    const response = await fetch(`${API_BASE}/analyze-input`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mode: inputMode,
        data: data,
        preferences: {
          diet: prefs.diet,
          timeLimit: prefs.timeLimit,
          calories: prefs.calories,
          servings: prefs.servings
        },
        current_inventory: currentInventory
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Backend error: ${response.status}`);
    }
    
    const result: ChefResponse = await response.json();
    return result;
    
  } catch (error) {
    console.error("ChefByte Backend Error:", error);
    throw error;
  }
};

/**
 * Generate alternative recipes excluding previously shown ones
 */
export const generateAlternatives = async (
  detectedIngredients: string[],
  prefs: UserPreferences,
  excludeTitles: string[]
): Promise<ChefResponse> => {
  
  try {
    const response = await fetch(`${API_BASE}/generate-alternatives`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ingredients: detectedIngredients,
        preferences: {
          diet: prefs.diet,
          timeLimit: prefs.timeLimit,
          calories: prefs.calories,
          servings: prefs.servings
        },
        exclude_titles: excludeTitles
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Backend error: ${response.status}`);
    }
    
    const result: ChefResponse = await response.json();
    return result;
    
  } catch (error) {
    console.error("ChefByte Backend Error:", error);
    throw error;
  }
};

/**
 * Health check endpoint to verify backend is running
 */
export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    return data.status === 'healthy' && data.agent_status === 'active';
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
};
