
import { GoogleGenAI, Type, Schema } from "@google/genai";
import { UserPreferences, ChefResponse } from "../types";

const genAI = new GoogleGenAI({ apiKey: process.env.API_KEY });

const responseSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    detectedIngredients: {
      type: Type.ARRAY,
      items: { type: Type.STRING },
      description: "List of ingredients detected from the image or text input.",
    },
    receiptData: {
      type: Type.OBJECT,
      properties: {
        storeName: { type: Type.STRING, description: "Name of the store if visible on receipt." },
        date: { type: Type.STRING, description: "Date of purchase if visible." },
        total: { type: Type.STRING, description: "Total amount paid if visible (e.g. $24.50)." },
      },
      description: "Extracted metadata if the input is a grocery receipt. Null otherwise.",
    },
    reasoning: {
      type: Type.STRING,
      description: "A short, agentic explanation of why these recipes were selected based on the ingredients and preferences.",
    },
    recipes: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          id: { type: Type.STRING },
          title: { type: Type.STRING },
          description: { type: Type.STRING },
          time: { type: Type.STRING },
          baseServings: { 
            type: Type.NUMBER, 
            description: "The number of servings this recipe is designed for (e.g. 2, 4)." 
          },
          ingredients: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: "List of ingredients with quantities (e.g. '2 eggs', '200g Chicken').",
          },
          steps: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: "Step-by-step cooking instructions.",
          },
          nutrition: {
            type: Type.OBJECT,
            properties: {
              calories: { type: Type.NUMBER },
              protein: { type: Type.STRING },
              carbs: { type: Type.STRING },
              fats: { type: Type.STRING },
            },
            required: ["calories", "protein", "carbs", "fats"],
          },
          matchScore: { type: Type.NUMBER, description: "Percentage match based on available ingredients (0-100)." },
        },
        required: ["id", "title", "description", "time", "baseServings", "ingredients", "steps", "nutrition", "matchScore"],
      },
    },
  },
  required: ["detectedIngredients", "reasoning", "recipes"],
};

export const generateMealPlan = async (
  inputMode: 'image' | 'text',
  data: string, // base64 image or text string
  prefs: UserPreferences,
  excludeRecipeTitles: string[] = [],
  currentInventory: string[] = []
): Promise<ChefResponse> => {
  
  const model = "gemini-2.5-flash";
  
  let systemPrompt = `
    You are ChefByte, an advanced culinary AI agent. 
    Your goal is to analyze inputs (images of fridges/receipts or text lists) to identify ingredients.
    Then, act as a world-class chef and nutritionist to suggest recipes.
    
    User Preferences:
    - Diet: ${prefs.diet}
    - Max Cooking Time: ${prefs.timeLimit}
    - Target Calories per serving: approx ${prefs.calories}
    - Servings: ${prefs.servings}
    
    Current Inventory History:
    The user ALREADY has these ingredients from previous scans: ${currentInventory.join(", ")}.
    Combine any NEW ingredients detected in this input with the history to plan meals.

    If the input is an image, perform object detection or OCR to find food items.
    
    If the input is a RECEIPT:
    1. Extract the store name, date, and total price if visible.
    2. List the food items purchased.

    Suggest 3 distinct recipes that maximize the use of ALL available ingredients (History + New).
    Be creative but practical.
  `;

  if (excludeRecipeTitles.length > 0) {
    systemPrompt += `\n\nIMPORTANT: The user requested alternative recipes. DO NOT suggest these recipes again: ${excludeRecipeTitles.join(', ')}. Provide 3 TOTALLY NEW options.`;
  }

  let contents = [];

  if (inputMode === 'image') {
    // Clean the base64 string if it contains metadata header
    const cleanBase64 = data.includes('base64,') ? data.split('base64,')[1] : data;
    
    contents = [
      {
        inlineData: {
          mimeType: "image/jpeg", // Assuming jpeg for simplicity, gemini handles most
          data: cleanBase64
        }
      },
      {
        text: "Analyze this image. Identify all visible food ingredients. If it's a receipt, extract metadata. Then generate recipes."
      }
    ];
  } else {
    contents = [
      {
        text: `I have these new ingredients: ${data}. Generate recipes based on the system instructions.`
      }
    ];
  }

  try {
    const response = await genAI.models.generateContent({
      model,
      config: {
        systemInstruction: systemPrompt,
        responseMimeType: "application/json",
        responseSchema: responseSchema,
        temperature: 0.85, // Higher temperature for variety
      },
      contents: [{ parts: contents.map(c => c.inlineData ? { inlineData: c.inlineData } : { text: c.text }) }]
    });

    const text = response.text;
    if (!text) throw new Error("No response from ChefByte");
    
    return JSON.parse(text) as ChefResponse;
  } catch (error) {
    console.error("ChefByte Error:", error);
    throw error;
  }
};

export const generateAlternatives = async (
  detectedIngredients: string[],
  prefs: UserPreferences,
  excludeTitles: string[]
): Promise<ChefResponse> => {
  const ingredientsText = detectedIngredients.join(", ");
  // Pass empty array for history because 'detectedIngredients' already contains the full merged list in our App logic
  return generateMealPlan('text', ingredientsText, prefs, excludeTitles, []);
};
