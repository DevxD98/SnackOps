# PantryPilot 🍳🤖

An AI-powered meal planning agent that uses Google Gemini Pro and Gemini Vision to help you make the most of your ingredients.

## Project Description

PantryPilot is an intelligent agent that:

- 📸 Analyzes fridge photos to extract ingredients using Gemini Vision
- 🧾 Parses grocery receipts with OCR capabilities
- 🔤 Normalizes ingredient names for consistent matching
- 🔍 Searches and filters recipes from a database
- 📊 Calculates nutrition information and macros
- 🍽️ Plans meals based on dietary constraints and preferences
- 📝 Generates meal plans with detailed reasoning

## How the Agent Works

PantryPilot follows the **Reason → Act → Observe** loop:

1. **Reason**: The orchestrator analyzes the current state and decides which tool to use next
2. **Act**: The selected tool is executed (e.g., extract ingredients, search recipes, calculate nutrition)
3. **Observe**: Results are added to memory, and the agent decides if more actions are needed

This continues until a complete meal plan is generated with full reasoning.

## Tool Overview

### 1. Vision Tool (`vision_tool.py`)

Uses Gemini Vision to analyze fridge photos and extract visible ingredients.

### 2. Receipt OCR Tool (`receipt_ocr_tool.py`)

Processes grocery receipt images to extract purchased items and quantities.

### 3. Ingredient Normalizer (`ingredient_normalizer.py`)

Standardizes ingredient names (e.g., "tomatos" → "tomatoes", "chicken breast" → "chicken").

### 4. Recipe Search (`recipe_search.py`)

Filters recipes from a CSV database based on available ingredients and dietary constraints.

### 5. Nutrition Estimator (`nutrition_estimator.py`)

Calculates nutritional information (calories, protein, carbs, fats) for recipes and meal plans.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Key Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### 3. Run the Project

#### Option 1: Gradio UI

```bash
python ui/gradio_ui.py
```

#### Option 2: Jupyter Notebook

```bash
jupyter notebook notebook/PantryPilot_Demo.ipynb
```

#### Option 3: Python Script

```python
from agent.orchestrator import PantryPilotAgent

agent = PantryPilotAgent()
result = agent.run(
    fridge_image="path/to/fridge.jpg",
    dietary_constraints=["vegetarian"],
    meal_count=3
)
print(result)
```

## Project Structure

```
PantryPilot/
├── README.md
├── requirements.txt
├── gemini_setup.py          # Centralized Gemini API configuration
├── agent/
│   ├── orchestrator.py      # Main agent orchestration logic
│   ├── memory.py            # Agent memory and state management
│   └── tools/
│       ├── vision_tool.py            # Gemini Vision for fridge photos
│       ├── receipt_ocr_tool.py       # Receipt parsing
│       ├── ingredient_normalizer.py  # Ingredient standardization
│       ├── recipe_search.py          # Recipe filtering
│       └── nutrition_estimator.py    # Nutrition calculations
├── data/
│   ├── recipes.csv          # Recipe database
│   └── nutrition.csv        # Nutrition information
├── notebook/
│   └── PantryPilot_Demo.ipynb
└── ui/
    └── gradio_ui.py         # Interactive web interface
```

## Example Usage

```python
# Create the agent
agent = PantryPilotAgent()

# Process fridge image and plan meals
meal_plan = agent.run(
    fridge_image="my_fridge.jpg",
    receipt_image="receipt.jpg",  # Optional
    dietary_constraints=["gluten-free", "high-protein"],
    calorie_target=2000,
    meal_count=3
)

# View the generated plan
print(meal_plan["reasoning"])
print(meal_plan["meals"])
print(meal_plan["nutrition_summary"])
```

## Future Improvements

- [ ] Add support for multiple fridge images
- [ ] Implement shopping list generation for missing ingredients
- [ ] Add meal prep time estimation
- [ ] Support for custom recipe additions
- [ ] Integration with fitness tracking apps
- [ ] Multi-day meal planning
- [ ] Cost optimization based on ingredient prices
- [ ] Seasonal ingredient recommendations
- [ ] Allergen detection and warnings
- [ ] Recipe difficulty ratings
- [ ] Leftover tracking and suggestions

## Technologies Used

- **Google Gemini Pro**: For reasoning and orchestration
- **Google Gemini Vision**: For image analysis
- **Gradio**: Interactive web UI
- **Pandas**: Data processing
- **OpenCV**: Image preprocessing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
