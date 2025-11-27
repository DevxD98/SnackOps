
export enum DietType {
  ANY = 'Anything',
  VEGETARIAN = 'Vegetarian',
  VEGAN = 'Vegan',
  NON_VEG = 'Non-Vegetarian',
  KETO = 'Keto',
  PALEO = 'Paleo'
}

export interface UserPreferences {
  diet: DietType;
  timeLimit: string; // e.g. "30 minutes"
  calories: number; // e.g. 600
  servings: number;
}

export interface Nutrition {
  calories: number;
  protein: string;
  carbs: string;
  fats: string;
}

export interface Recipe {
  id: string;
  title: string;
  description: string;
  time: string;
  baseServings: number;
  ingredients: string[];
  steps: string[];
  nutrition: Nutrition;
  matchScore: number; // 0-100 based on ingredient availability
}

export interface ReceiptData {
  storeName?: string;
  date?: string;
  total?: string;
}

export interface ChefResponse {
  detectedIngredients: string[];
  receiptData?: ReceiptData;
  reasoning: string;
  recipes: Recipe[];
}

export type InputMode = 'fridge' | 'receipt' | 'text';

export type AppState = 'idle' | 'analyzing' | 'results' | 'error';
