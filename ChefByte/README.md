# ChefByte 🍳🤖

### AI-Powered Meal Planning Agent for Indian Households

**Powered by Google ADK & Gemini**

ChefByte is an intelligent meal planning assistant that uses Google's Agent Development Kit (ADK) and Gemini 2.5 Flash to help Indian households make the most of their ingredients with vision analysis, recipe search, and nutrition planning.

## 🎯 Project Description

ChefByte combines **multi-modal AI** capabilities to provide:

- 📸 **Vision Analysis**: Extract ingredients from fridge photos using Gemini Vision
- 🍛 **Recipe Search**: Find recipes matching available ingredients with dietary filters
- 📊 **Nutrition Tracking**: Calculate calories, protein, carbs, and macros
- 🍽️ **Meal Planning**: Generate balanced meal plans with calorie targets
- 🌶️ **Indian Specialization**: Optimized for Indian recipes, ingredients, and regional cuisines
- 🗣️ **Multi-lingual**: Support for Hindi and English ingredient names

## 🏗️ Architecture

ChefByte uses **Google ADK's ReAct pattern** (Reasoning + Acting):

```
User Query → ADK Agent → ReAct Loop → Response
                ↓
        ┌───────┴────────┐
        │  System Prompt │
        │  (Indian Focus)│
        └───────┬────────┘
                ↓
        ┌───────────────────┐
        │   3 Tools         │
        ├───────────────────┤
        │ 1. Vision Tool    │
        │ 2. Recipe Search  │
        │ 3. Nutrition Est. │
        └───────────────────┘
```

### ReAct Loop:

1. **Reason**: Agent analyzes query and decides which tool to use
2. **Act**: Tool is executed with appropriate parameters
3. **Observe**: Results inform next decision
4. **Repeat**: Until user's request is fully satisfied

## 🛠️ Tools

### 1. Vision Tool (`vision_tool.py`)

- Extracts ingredients from fridge photos
- Handles Hindi/English text recognition
- Identifies vegetables, fruits, dairy, grains, spices
- **FunctionTool**: `extract_ingredients_from_image(image_path, image_type)`

### 2. Recipe Search (`recipe_search_adk.py`)

- Filters 10,000+ Indian recipes
- Matches available ingredients (calculates match %)
- Supports dietary filters: vegetarian, vegan, jain, halal, gluten-free
- Regional cuisines: Punjabi, South Indian, Bengali, Gujarati, etc.
- **FunctionTool**: `search_recipes(available_ingredients, dietary_constraints, max_missing, cuisine_type)`

### 3. Nutrition Estimator (`nutrition_estimator_adk.py`)

- Calculates calories, protein, carbs, fats
- Selects optimal meals for calorie targets
- Generates personalized recommendations
- Tracks macros across meal plans
- **FunctionTool**: `estimate_nutrition(recipes, calorie_target, meal_count, protein_target)`

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (tested on 3.12.9)
- Google API Key with Gemini access
- macOS/Linux (Windows with WSL)

### 1. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd ChefByte

# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:

- `google-adk==1.18.0` (Agent Development Kit)
- `google-generativeai` (Gemini API)
- `gradio` (UI framework)
- `pandas` (Data processing)
- `Pillow` (Image handling)

### 3. Configure API Key

Create `.env` file:

```bash
GOOGLE_API_KEY=your_api_key_here
```

Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 4. Run ChefByte

#### Option A: Gradio Web UI (Recommended)

```bash
python ui/gradio_adk_ui.py
```

Then open: http://localhost:7860

#### Option B: Command Line Test

```bash
python quick_test_adk.py
```

#### Option C: Jupyter Notebook Demo

```bash
jupyter notebook ChefByte_Demo.ipynb
```

## 📖 Usage Examples

### Text Query

```
User: I have tomatoes, onions, and rice. What can I cook?
ChefByte: Based on your ingredients, here are 3 recipes...
```

### Image Analysis

```
User: [uploads fridge photo]
ChefByte: I can see: tomatoes, paneer, spinach, onions...
          Suggested recipes: Palak Paneer, Paneer Bhurji...
```

### Meal Planning

```
User: Create a 1800 calorie meal plan with 3 vegetarian meals
ChefByte: Here's your plan:
          - Breakfast: Poha (350 cal, 12g protein)
          - Lunch: Dal Rice (600 cal, 20g protein)
          - Dinner: Paneer Tikka (850 cal, 35g protein)
```

## 📁 Project Structure

```
ChefByte/
├── README.md
├── requirements.txt
├── .env                          # API keys (not in repo)
│
├── adk_agent/                    # Google ADK Implementation
│   ├── __init__.py
│   ├── chefbyte_agent.py         # Main ADK Agent with Runner
│   ├── config.yaml               # Agent configuration
│   ├── prompts/
│   │   └── system_prompt.md      # Indian-optimized system prompt
│   └── tools/                    # ADK FunctionTools
│       ├── __init__.py
│       ├── vision_tool.py        # Gemini Vision ingredient extraction
│       ├── recipe_search_adk.py  # Recipe matching & filtering
│       └── nutrition_estimator_adk.py  # Nutrition calculation
│
├── ui/                           # User Interfaces
│   └── gradio_adk_ui.py          # Multi-modal Gradio web UI
│
├── data/                         # Databases
│   ├── recipes.csv               # 10,000+ Indian recipes
│   └── nutrition.csv             # Nutrition data
│
├── test_data/                    # Test assets
│   └── images/
│       └── fridge_sample.jpg
│
├── tests/                        # Test scripts
│   ├── verify_setup.py           # Setup validation
│   ├── quick_test_adk.py         # Single query test
│   └── test_chefbyte_adk.py      # Full test suite
│
├── ChefByte_Demo.ipynb           # Interactive demo notebook
└── TESTING.md                    # Testing guide
```

## 🧪 Testing

### Verify Installation

```bash
python verify_setup.py
```

Expected output:

```
✓ ADK imports working
✓ Gemini setup successful
✓ Vision tool loaded
✓ Agent created with 3 tools
ALL CHECKS PASSED ✓
```

### Quick Test

```bash
python quick_test_adk.py
```

### Full Test Suite

```bash
python tests/test_chefbyte_adk.py
```

See [TESTING.md](TESTING.md) for detailed testing guide.

## 🎨 Features

### Multi-Modal Input

- ✅ Text queries (natural language)
- ✅ Image upload (fridge photos)
- 🔄 Voice input (coming soon)

### Dietary Support

- Vegetarian, Vegan, Jain, Halal
- Gluten-free, Dairy-free, Nut-free
- High-protein, Low-carb, Keto

### Regional Cuisines

- Punjabi, South Indian, Bengali
- Gujarati, Maharashtrian, Rajasthani
- Goan, Kashmiri, Kerala, Tamil

### Smart Features

- Ingredient matching (fuzzy match)
- Missing ingredient suggestions
- Ingredient substitution recommendations
- Calorie & macro tracking
- Meal plan optimization
- Hindi/English ingredient support

## 🔧 Configuration

Edit `adk_agent/config.yaml`:

```yaml
model:
  name: gemini-2.5-flash
  temperature: 0.7

agent:
  max_iterations: 10
  indian_focus: true
  regional_preferences:
    - punjabi
    - south_indian
    - bengali
```

## 📊 Performance

- **Average Response Time**: ~2-3 seconds
- **Vision Analysis**: ~3-5 seconds
- **Recipe Search**: ~1-2 seconds (10,000+ recipes)
- **Nutrition Calculation**: <1 second

## 🐛 Troubleshooting

### Import Errors

```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### API Key Issues

```bash
# Check .env file exists
cat .env

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GOOGLE_API_KEY'))"
```

### Tool Not Found

```bash
# Verify agent initialization
python verify_setup.py
```

## 🤝 Contributing

Built for **Google ADK Hackathon 2025**

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- **Google ADK Team** for the amazing Agent Development Kit
- **Gemini Team** for powerful AI models
- **Indian Food Community** for recipe inspiration

## 📧 Contact

Questions? Reach out via GitHub issues or email.

---

<center>

**Made with ❤️ for Indian Households**

_ChefByte - Your AI Sous Chef_ 🍳

</center>
├── notebook/
│   └── ChefByte_Demo.ipynb
└── ui/
    └── gradio_ui.py         # Interactive web interface
```

## Example Usage

```python
# Create the agent
agent = ChefByteAgent()

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
