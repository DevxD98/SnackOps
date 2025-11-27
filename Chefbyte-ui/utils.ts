
import { 
  Carrot, Beef, Fish, Milk, Egg, Apple, Wheat, Drumstick, Ham, 
  Pizza, Sandwich, Soup, Cookie, Cake, Croissant, Coffee, Beer, 
  Wine, Martini, Popcorn, Candy, IceCream, Lollipop, Salad, 
  Bean, Leaf, Droplets, Utensils, Cherry, Banana, Grape, Citrus
} from 'lucide-react';
import React from 'react';

// --- Ingredient Scaling Logic ---

const FRACTION_MAP: Record<string, number> = {
  '1/2': 0.5, '1/3': 0.33, '1/4': 0.25, '3/4': 0.75, '2/3': 0.66, '1/8': 0.125
};

export const parseIngredientQuantity = (ingredient: string): { value: number | null, text: string } => {
  // Try to match "1.5 cups", "1/2 tsp", "2 eggs"
  // Regex matches start of string: number/fraction/range
  const regex = /^(\d+(?:\.\d+)?|\d+\/\d+|\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)\s+(.*)/;
  const match = ingredient.trim().match(regex);

  if (!match) return { value: null, text: ingredient };

  let numStr = match[1];
  const rest = match[2];

  let value: number = 0;

  if (numStr.includes('-')) {
    // Handle ranges "1-2" -> 1.5
    const [start, end] = numStr.split('-').map(Number);
    value = (start + end) / 2;
  } else if (numStr.includes('/')) {
    // Handle fractions "1/2"
    const [num, den] = numStr.split('/').map(Number);
    value = num / den;
  } else {
    value = parseFloat(numStr);
  }

  return { value, text: rest };
};

export const formatQuantity = (value: number): string => {
  // Round to reasonable decimals
  if (Math.abs(value % 1) < 0.05) return Math.round(value).toString();
  
  // Check for common fractions
  const decimal = value % 1;
  if (Math.abs(decimal - 0.5) < 0.1) return Math.floor(value) === 0 ? "1/2" : `${Math.floor(value)}.5`;
  if (Math.abs(decimal - 0.25) < 0.1) return Math.floor(value) === 0 ? "1/4" : `${Math.floor(value)}.25`;
  if (Math.abs(decimal - 0.33) < 0.1) return Math.floor(value) === 0 ? "1/3" : `${Math.floor(value)}.33`;
  if (Math.abs(decimal - 0.75) < 0.1) return Math.floor(value) === 0 ? "3/4" : `${Math.floor(value)}.75`;

  return value.toFixed(1).replace(/\.0$/, '');
};

export const scaleIngredientText = (ingredient: string, factor: number): string => {
  if (factor === 1) return ingredient;
  
  const { value, text } = parseIngredientQuantity(ingredient);
  if (value === null) return ingredient; // Could not parse number

  const scaledValue = value * factor;
  return `${formatQuantity(scaledValue)} ${text}`;
};


// --- Icon Mapping Logic ---

export const getIngredientIcon = (name: string) => {
  const lower = name.toLowerCase();
  
  if (lower.match(/carrot|veg|spinach|broccoli|cucumber|kale|lettuce/)) return Carrot;
  if (lower.match(/beef|steak|meat|pork|lamb|sausage|bacon/)) return Beef;
  if (lower.match(/chicken|turkey|duck|poultry/)) return Drumstick;
  if (lower.match(/fish|salmon|tuna|seafood|shrimp|crab|lobster/)) return Fish;
  if (lower.match(/milk|cream|yogurt|cheese|dairy|butter/)) return Milk;
  if (lower.match(/egg|omelet/)) return Egg;
  if (lower.match(/apple|fruit|pear|peach|plum/)) return Apple;
  if (lower.match(/banana/)) return Banana;
  if (lower.match(/grape|berry/)) return Grape;
  if (lower.match(/lemon|lime|orange|citrus/)) return Citrus;
  if (lower.match(/cherry/)) return Cherry;
  if (lower.match(/bread|toast|flour|wheat|grain|pasta|noodle|rice/)) return Wheat;
  if (lower.match(/pizza/)) return Pizza;
  if (lower.match(/sandwich|burger/)) return Sandwich;
  if (lower.match(/soup|stew|broth/)) return Soup;
  if (lower.match(/cookie|biscuit/)) return Cookie;
  if (lower.match(/cake|muffin|pastry|pie/)) return Cake;
  if (lower.match(/croissant/)) return Croissant;
  if (lower.match(/coffee|tea|espresso/)) return Coffee;
  if (lower.match(/beer|ale/)) return Beer;
  if (lower.match(/wine/)) return Wine;
  if (lower.match(/alcohol|drink|cocktail/)) return Martini;
  if (lower.match(/corn|popcorn/)) return Popcorn;
  if (lower.match(/candy|sugar|chocolate|sweet/)) return Candy;
  if (lower.match(/ice cream|gelato/)) return IceCream;
  if (lower.match(/salad/)) return Salad;
  if (lower.match(/bean|legume|pea|lentil|tofu|soy/)) return Bean;
  if (lower.match(/water|oil|sauce|liquid|vinegar/)) return Droplets;
  if (lower.match(/ham|salami/)) return Ham;
  if (lower.match(/herb|spice|leaf|basil|mint/)) return Leaf;

  return Utensils; // Default
};
