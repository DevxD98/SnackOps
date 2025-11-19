# ChefByte 🍳 | SnackOps Project

### AI-Powered Meal Planning Assistant for Indian Households

**Built with Google Agentic Development Kit (ADK) & Gemini 2.5 Flash**

> An intelligent meal planning companion that transforms your fridge contents into personalized meal plans using advanced multi-modal AI capabilities.

[![Made with Google ADK](https://img.shields.io/badge/Made%20with-Google%20ADK-4285F4?style=for-the-badge&logo=google)](https://github.com/google/adk)
[![Powered by Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.5-8E75B2?style=for-the-badge)](https://deepmind.google/technologies/gemini/)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-FF6B35?style=for-the-badge)](https://gradio.app/)

---

## 🎯 Overview

**ChefByte** is part of the **SnackOps** project, an intelligent meal planning solution built using **Google's Agentic Development Kit (ADK)**. It leverages the power of **Gemini 2.5 Flash** to provide:

- **Vision-Powered Ingredient Detection** - Scan your fridge and automatically extract ingredients
- **Smart Recipe Matching** - Find recipes from 6,889+ Indian & international dishes
- **Nutrition Intelligence** - Track calories, macros, and create balanced meal plans
- **Personalized Recommendations** - Dietary preferences, cuisine types, and health goals
- **Persistent Memory** - Remembers your preferences, favorites, and cooking history

### What Makes ChefByte Special?

✨ **Agentic AI Architecture** - Uses Google ADK's autonomous agent framework with tool-calling capabilities  
🇮🇳 **Indian Household Optimized** - Specialized for Indian ingredients, recipes, and regional cuisines  
🖼️ **Multi-Modal Interface** - Fullscreen UI with vision, text, and structured inputs  
🧠 **Persistent Memory** - Tracks your fridge inventory, preferences, and cooking history  
📊 **Beautiful Recipe Templates** - Magazine-quality recipe presentations with nutrition facts

---

## ✨ Key Features

### 1. **Visual Ingredient Detection** 🔍

- Upload fridge/pantry photos via webcam or file upload
- AI-powered ingredient extraction using Gemini Vision
- Clean, tag-based ingredient display
- Automatic sync across all tabs (Chat, Fridge Scanner, Meal Planner)

### 2. **Smart Recipe Generation** 🍽️

- **Flexible ingredient matching** - Works with 1-2 ingredients or full pantry
- **Beautiful recipe templates** - Nutrition facts, cooking steps, chef's tips
- **Dietary filters** - Vegetarian, Non-Vegetarian, Vegan, Gluten-Free, Jain
- **Cuisine preferences** - Indian, Punjabi, South Indian, Bengali, International
- **Auto-adjusting search** - More flexible with fewer ingredients

### 3. **Interactive Chat Assistant** 💬

- Natural language conversation
- Ingredient sidebar with quick actions
- One-click recipe suggestions
- Add selected ingredients to message
- Dietary and cuisine filters built-in

### 4. **Personalized Meal Planner** 📅

- Select ingredients from scanned inventory
- Set calorie targets and meal counts
- Dietary constraints support
- Generates complete meal plans with nutrition breakdown

### 5. **Persistent Memory System** 🧠

- Fridge inventory tracking
- Cooking history (recent recipes, favorites, dislikes)
- Dietary preferences and allergens
- Calorie targets and health goals
- Multi-user support

---

## 🏗️ Architecture

ChefByte is built on **Google's Agentic Development Kit (ADK)**, which enables autonomous agent behavior with tool-calling capabilities.

### Agentic Framework

```
┌─────────────────────────────────────────────────────────┐
│                    User Input                           │
│  (Text Query / Fridge Photo / Structured Form)          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│            ChefByteADKAgent (Orchestrator)              │
│  ┌────────────────────────────────────────────────┐    │
│  │  Enhanced System Prompt                         │    │
│  │  • Indian household focus                       │    │
│  │  • Beautiful recipe templates                   │    │
│  │  • Memory context injection                     │    │
│  │  • Flexible ingredient handling                 │    │
│  └────────────────────────────────────────────────┘    │
│                         │                               │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │       Gemini 2.5 Flash (Function Calling)       │   │
│  │  Autonomous decision-making and tool selection  │   │
│  └────────┬──────────────────────┬──────────────────┘   │
│           │                      │                      │
│           ▼                      ▼                      │
│  ┌────────────────┐    ┌────────────────────────┐      │
│  │  Tool Router   │    │  Persistent Memory     │      │
│  └────────┬───────┘    └────────────────────────┘      │
│           │                                             │
└───────────┼─────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────┐
│                   Tool Ecosystem                       │
├───────────────────────────────────────────────────────┤
│                                                        │
│  1️⃣  Vision Tool (extract_ingredients_from_image)     │
│      • Gemini Vision API                              │
│      • Image preprocessing                            │
│      • Ingredient normalization                       │
│                                                        │
│  2️⃣  Recipe Search (search_recipes)                   │
│      • 6,889 recipes database                         │
│      • Fuzzy ingredient matching                      │
│      • Dietary & cuisine filtering                    │
│      • Smart scoring algorithm                        │
│                                                        │
│  3️⃣  Nutrition Estimator (estimate_nutrition)         │
│      • Calorie & macro calculation                    │
│      • Meal plan optimization                         │
│      • Nutrition goal tracking                        │
│                                                        │
└───────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────┐
│               Response Generation                      │
│  • Formatted recipes (Markdown templates)             │
│  • Meal plans with nutrition breakdown                │
│  • Ingredient lists with availability status          │
│  • Chef's tips and substitutions                      │
└───────────────────────────────────────────────────────┘
```

### Agent Workflow

1. **Input Processing** - User query, image, or form data received
2. **Memory Enhancement** - System prompt enriched with user context (fridge, preferences, history)
3. **Autonomous Decision** - Gemini decides which tool(s) to call based on the query
4. **Tool Execution** - Agent executes selected tools with appropriate parameters
5. **Memory Update** - Results stored in persistent memory for future context
6. **Response Formatting** - Beautiful templates for recipes/meal plans
7. **User Delivery** - Rendered in Gradio UI

### Key Components

- **ChefByteADKAgent** - Main orchestrator using direct Gemini client with function calling
- **FunctionTools** - Three specialized tools registered with the agent
- **PersistentMemory** - JSON-backed per-user storage system
- **Enhanced Search** - Auto-adjusting `max_missing` based on ingredient count
- **Gradio UI** - Fullscreen multi-tab interface with ingredient sync

---

## 🛠️ Tools

### 1. Vision Tool (`vision_tool.py`)

Extracts ingredients from fridge/pantry photos using Gemini Vision

**Capabilities:**

- Multi-modal image analysis
- Hindi/English text recognition
- Identifies vegetables, fruits, dairy, grains, spices
- Normalizes ingredient names

**FunctionTool Declaration:**

```python
extract_ingredients_from_image(
    image_path: str,
    image_type: str = "fridge"
) -> dict
```

### 2. Recipe Search (`recipe_search_adk.py`)

Fuzzy matching engine for 6,889+ recipes with intelligent scoring

**Capabilities:**

- Ingredient matching with auto-adjusted `max_missing`
  - 1-3 ingredients → max_missing: 8 (very flexible)
  - 4-5 ingredients → max_missing: 6
  - 6+ ingredients → user specified
- Dietary filters: Vegetarian, Non-Veg, Vegan, Gluten-Free, Jain
- Regional cuisines: Indian, Punjabi, South Indian, Bengali, International
- Smart scoring algorithm with substring matching

**FunctionTool Declaration:**

```python
search_recipes(
    available_ingredients: list[str],
    dietary_constraints: str = "Any",
    max_missing: int = 5,
    cuisine_type: str = "Any"
) -> list[dict]
```

### 3. Nutrition Estimator (`nutrition_estimator_adk.py`)

Calculates nutrition facts and optimizes meal plans

**Capabilities:**

- Calorie, protein, carbs, fat calculation
- Meal plan optimization for calorie targets
- Macro tracking across multiple meals
- Personalized nutrition recommendations

**FunctionTool Declaration:**

```python
estimate_nutrition(
    recipes: list[dict],
    calorie_target: int = 2000,
    meal_count: int = 3,
    protein_target: int = None
) -> dict
```

---

## 🖼️ User Interface

### Fullscreen Gradio UI (Port 7860)

**3-Tab Layout:**

#### 1. Chat Assistant

- **Main Chat Panel (70%)** - Natural language conversation with agent
- **Ingredient Sidebar (30%)** - Interactive ingredient selector
  - Checkboxes for scanned ingredients
  - Dietary & cuisine filters
  - "Add Selected to Message" button
  - "Get Recipe Suggestions" one-click button

#### 2. Fridge Scanner

- **Image Upload** - Webcam or file input
- **Scan Button** - Triggers Gemini Vision extraction
- **Results:**
  - Agent Response (conversational message)
  - Detected Ingredients (clean checkboxes)
- **Generate Recipes** - Redirects to Chat Assistant with context

#### 3. Meal Planner

- **Ingredient Selector** - Checkboxes synced from scanner
- **Manual Entry** - Accordion fallback for typing ingredients
- **Preferences:**
  - Dietary constraints dropdown
  - Calorie target (1200-3000)
  - Number of meals (1-5)
- **Generate Meal Plan** - Creates complete daily plan with nutrition

### 3-Way Ingredient Sync

Scanning fridge **automatically updates checkboxes** in:

- Fridge Scanner tab ✅
- Chat Assistant sidebar ✅
- Meal Planner selector ✅

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (tested on 3.12.9)
- Google API Key with Gemini access
- macOS/Linux/Windows (WSL)
- 2GB+ RAM

### 1. Clone Repository

```bash
git clone https://github.com/DevxD98/SnackOps.git
cd SnackOps/ChefByte
```

### 2. Setup Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**

- `google-adk==1.18.0` - Agentic Development Kit
- `google-generativeai` - Gemini API client
- `gradio==5.49.1` - Web UI framework
- `pandas` - Data processing
- `Pillow` - Image handling
- `python-dotenv` - Environment variables

### 4. Configure API Key

Create `.env` file in the ChefByte directory:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

### 5. Launch ChefByte

```bash
python ui/gradio_adk_ui.py
```

Open http://localhost:7860 in your browser 🎉

---

## 📚 Usage Guide

### Option 1: Fridge Scanner Workflow

1. **Go to "Fridge Scanner" tab**
2. **Upload photo** of your fridge/pantry (webcam or file)
3. **Click "Scan for Ingredients"** - AI extracts ingredients
4. **View results:**
   - Agent Response: Conversational message
   - Detected Ingredients: Clean checkboxes
5. **Select/deselect** ingredients you want to use
6. **Set filters** (dietary, cuisine)
7. **Click "Generate Recipes"** → Redirects to Chat Assistant with recipes!

### Option 2: Chat Assistant Workflow

1. **Go to "Chat Assistant" tab**
2. **See ingredient sidebar** (synced from fridge scan)
3. **Option A - Quick Recipe:**
   - Select ingredients in sidebar
   - Choose filters
   - Click "Get Recipe Suggestions" → Instant recipes!
4. **Option B - Custom Message:**
   - Select ingredients
   - Click "Add Selected to Message"
   - Edit the auto-generated prompt
   - Send!
5. **Option C - Free Chat:**
   - Type naturally: "I have eggs and tomatoes. What can I cook?"

### Option 3: Meal Planner Workflow

1. **Go to "Meal Planner" tab**
2. **See ingredient checkboxes** (synced from fridge scan)
3. **Select ingredients** or enter manually
4. **Set preferences:**
   - Dietary constraints
   - Calorie target
   - Number of meals
5. **Click "Generate Meal Plan"** → Complete plan with nutrition!

### Example Queries

```
"I have 2 eggs, make me an Indian recipe"
"Suggest 3 vegetarian recipes using tomatoes and onions"
"Create a 1800 calorie meal plan for today"
"What's a quick breakfast I can make with bread and eggs?"
```

---

## 📁 Project Structure

```
ChefByte/
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env                             # API keys (gitignored)
│
├── adk_agent/                       # Agentic core (Google ADK)
│   ├── __init__.py
│   ├── chefbyte_agent.py            # Main ADK agent orchestrator
│   ├── config.yaml                  # Agent configuration
│   ├── persistent_memory.py         # Memory system
│   ├── prompts/
│   │   └── system_prompt.md         # Enhanced system prompt
│   └── tools/                       # FunctionTools
│       ├── __init__.py
│       ├── vision_tool.py           # Gemini Vision (ingredient extraction)
│       ├── recipe_search_adk.py     # Recipe matching & scoring
│       └── nutrition_estimator_adk.py  # Nutrition calculation
│
├── ui/
│   └── gradio_adk_ui.py             # Fullscreen Gradio UI
│
├── data/                            # Datasets
│   ├── recipes.csv                  # 6,889 recipes
│   ├── nutrition.csv                # Nutrition data
│   ├── memory/                      # User memory (JSON files)
│   │   ├── default_user_fridge.json
│   │   ├── default_user_history.json
│   │   └── default_user_preferences.json
│   └── raw/                         # Raw datasets
│       ├── indian_recipes_raw.csv
│       └── better_recipes_raw.csv
│
├── scripts/
│   ├── merge_local_recipes.py       # Recipe data transformation
│   └── import_kaggle_recipes.py     # Dataset import
│
├── tests/
│   ├── test_new_recipes.py          # Recipe search validation
│   └── test_memory_system.py        # Memory system tests
│
└── bolt/                            # Alternative Vite UI (optional)
    └── src/
```

---

## 🔧 Technologies Used

### AI & Agentic Framework

- **Google Agentic Development Kit (ADK) 1.18.0** - Agent orchestration framework
- **Gemini 2.5 Flash** - LLM with function calling
- **Gemini Vision** - Multi-modal image understanding

### Backend

- **Python 3.12+** - Core language
- **Pandas** - Data processing (6,889 recipes)
- **Python-dotenv** - Environment management

### Frontend

- **Gradio 5.49.1** - Web UI framework
- **Custom Theme** - Emerald/Amber color scheme
- **Fullscreen Layout** - Responsive design (max-width: 100%)

### Data

- **CSV Databases** - Recipes & nutrition data
- **JSON Storage** - Persistent user memory
- **Kaggle Datasets** - Indian & international recipes

### Features

- **Function Calling** - Agent tool selection
- **Persistent Memory** - Multi-user support
- **Fuzzy Matching** - Flexible ingredient search
- **Auto-adjusting Search** - Dynamic `max_missing` parameter
- **Beautiful Templates** - Markdown recipe formatting

---

## 🧪 Development

### Run Tests

```bash
# Test recipe search
python tests/test_new_recipes.py

# Test memory system
python tests/test_memory_system.py
```

### Add New Recipes

1. Place CSV in `data/raw/`
2. Update `scripts/merge_local_recipes.py`
3. Run: `python scripts/merge_local_recipes.py`

### Modify Agent Behavior

Edit `adk_agent/prompts/system_prompt.md` for:

- Personality changes
- Recipe template formatting
- Instruction emphasis

### Add New Tools

1. Create tool in `adk_agent/tools/`
2. Register in `chefbyte_agent.py` → `_prepare_tools()`
3. Add function declaration with schema

---

## 🤝 Contributing

Built for **SnackOps Project** and **Google ADK Exploration**

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Test thoroughly before PR
- Update README if adding features

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- **Google ADK Team** - For the powerful Agentic Development Kit
- **Google Gemini Team** - For state-of-the-art AI models
- **Kaggle Community** - For recipe datasets
- **Indian Food Community** - For culinary inspiration

---

## 📧 Contact & Support

- **Project**: SnackOps / ChefByte
- **Developer**: DevxD98
- **GitHub**: [DevxD98/SnackOps](https://github.com/DevxD98/SnackOps)
- **Issues**: [Report bugs](https://github.com/DevxD98/SnackOps/issues)

---

<div align="center">

### Made with ❤️ for Indian Households

**ChefByte - Your AI Sous Chef** 🍳

_Powered by Google Agentic Development Kit & Gemini_

[⬆ Back to Top](#chefbyte---snackops-project)

</div>
