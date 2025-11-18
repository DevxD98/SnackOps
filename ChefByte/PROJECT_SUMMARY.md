# ChefByte - Project Summary

**Built for Google ADK Hackathon 2025**

## Overview

ChefByte is an AI-powered meal planning assistant specifically designed for Indian households. It uses Google's Agent Development Kit (ADK) and Gemini 2.5 Flash to provide multi-modal meal planning through vision analysis, recipe search, and nutrition tracking.

## Key Features

### 1. Multi-Modal Intelligence

- **Vision Analysis**: Extract ingredients from fridge photos
- **Text Queries**: Natural language meal planning
- **Voice Input**: Coming soon with Hindi/English support

### 2. Indian Household Optimization

- **Regional Cuisines**: Punjabi, South Indian, Bengali, Gujarati, etc.
- **Dietary Support**: Vegetarian, Vegan, Jain, Halal, Gluten-free
- **Bi-lingual**: Hindi and English ingredient recognition
- **Spice Profiles**: Understanding of Indian masalas and spices

### 3. Intelligent Agent Architecture

- **ReAct Pattern**: Reasoning + Acting loop for intelligent decision-making
- **3 Specialized Tools**:
  - Vision Tool: Gemini Vision for ingredient extraction
  - Recipe Search: 10,000+ Indian recipes with smart matching
  - Nutrition Estimator: Calorie and macro tracking

### 4. User-Friendly Interface

- **Gradio Web UI**: Clean, intuitive multi-tab interface
- **Chat Mode**: Conversational meal planning
- **Fridge Scanner**: Upload photos for instant analysis
- **Meal Planner**: Structured planning with targets

## Technical Stack

### Core Technologies

- **Google ADK 1.18.0**: Agent orchestration framework
- **Gemini 2.5 Flash**: Multi-modal AI model
- **Python 3.12+**: Modern Python with type hints
- **Gradio 5.0+**: Interactive web interface

### Architecture Pattern

```
User Input → ADK Agent → ReAct Loop → Tools → Response
                ↓
        System Prompt (Indian Focus)
                ↓
        3 FunctionTools
        ├─ Vision Tool
        ├─ Recipe Search
        └─ Nutrition Estimator
```

### ADK Integration

- **Agent**: Orchestrates tool selection and execution
- **Runner**: Manages async execution and session state
- **FunctionTool**: Wraps Python functions for agent use
- **InMemorySessionService**: Maintains conversation context

## Project Structure

```
ChefByte/
├── adk_agent/                    # ADK implementation
│   ├── chefbyte_agent.py         # Main agent with Runner
│   ├── config.yaml               # Agent configuration
│   ├── prompts/
│   │   └── system_prompt.md      # Indian-optimized prompt
│   └── tools/                    # 3 FunctionTools
│       ├── vision_tool.py
│       ├── recipe_search_adk.py
│       └── nutrition_estimator_adk.py
│
├── ui/                           # User interfaces
│   └── gradio_adk_ui.py          # Multi-modal web UI
│
├── data/                         # Databases
│   ├── recipes.csv               # 10,000+ recipes
│   └── nutrition.csv             # Nutrition data
│
├── tests/                        # Testing suite
│   ├── verify_setup.py
│   ├── quick_test_adk.py
│   └── test_chefbyte_adk.py
│
├── ChefByte_Demo.ipynb           # Interactive demo
├── TESTING.md                    # Testing guide
├── README.md                     # Documentation
└── requirements.txt              # Dependencies
```

## Implementation Details

### Tool 1: Vision Tool

**Purpose**: Extract ingredients from fridge photos

**Input**:

- `image_path`: Path to fridge/receipt image
- `image_type`: "fridge" or "receipt"

**Process**:

1. Load image using PIL
2. Send to Gemini Vision API
3. Parse response for ingredients
4. Normalize Hindi/English names
5. Return structured ingredient list

**Output**: List of ingredients with quantities (if visible)

### Tool 2: Recipe Search

**Purpose**: Find recipes matching available ingredients

**Input**:

- `available_ingredients`: List of ingredients
- `dietary_constraints`: Vegetarian, vegan, etc.
- `max_missing`: Maximum missing ingredients allowed
- `cuisine_type`: Regional preference

**Process**:

1. Load recipe database (10,000+ recipes)
2. Filter by dietary constraints
3. Filter by cuisine type
4. Calculate ingredient match percentage
5. Score and rank recipes
6. Return top 10 matches

**Output**: List of recipes with:

- Match percentage
- Missing ingredients
- Nutrition information
- Cooking time & difficulty

### Tool 3: Nutrition Estimator

**Purpose**: Calculate nutrition and optimize meal plans

**Input**:

- `recipes`: List of recipe candidates
- `calorie_target`: Daily calorie goal
- `meal_count`: Number of meals (1-5)
- `protein_target`: Protein goal (optional)

**Process**:

1. Load nutrition database
2. Estimate nutrition for each recipe
3. Select optimal meal combination
4. Calculate total macros
5. Generate personalized recommendations

**Output**:

- Selected meals
- Total calories, protein, carbs, fats
- Recommendations for balance

## ReAct Loop Example

**User Query**: "I have tomatoes, onions, rice, and paneer. Create a 1800 calorie meal plan."

**Loop Execution**:

1. **Reason**: Agent analyzes query → needs recipe search first
2. **Act**: Calls `search_recipes("tomatoes, onions, rice, paneer", "vegetarian", 2, null)`
3. **Observe**: Gets 10 matching recipes
4. **Reason**: Now needs nutrition calculation for meal planning
5. **Act**: Calls `estimate_nutrition(recipes, 1800, 3, null)`
6. **Observe**: Gets optimized 3-meal plan
7. **Reason**: Has all information needed
8. **Respond**: Returns complete meal plan with nutrition

## Key Innovations

### 1. Indian-Specific Optimization

- **Ingredient Aliases**: Maps "टमाटर" → "tomato", "pyaaz" → "onion"
- **Regional Recipes**: 10,000+ authentic Indian dishes
- **Spice Recognition**: Understands masala combinations
- **Dietary Compliance**: Jain (no onion/garlic), strict vegetarian

### 2. Smart Ingredient Matching

- **Fuzzy Matching**: Handles typos and variations
- **Category Matching**: "vegetables" matches tomato, onion, etc.
- **Substitution Suggestions**: Recommends alternatives for missing ingredients
- **Quantity-Aware**: Considers ingredient amounts when available

### 3. Context-Aware Planning

- **Session Memory**: Remembers previous conversation
- **User Preferences**: Learns dietary restrictions
- **Progressive Refinement**: Iterative meal plan adjustments
- **Multi-Turn Conversations**: Natural dialogue flow

### 4. Nutrition Intelligence

- **Database-First**: Uses accurate nutrition data when available
- **Smart Estimation**: Calculates for missing items
- **Macro Balancing**: Optimizes protein/carbs/fats
- **Calorie Targeting**: Respects user goals

## Testing Strategy

### Level 1: Unit Testing

- Test each tool independently
- Validate input/output formats
- Check error handling

### Level 2: Integration Testing

- Test agent with all 3 tools
- Verify ReAct loop execution
- Check session management

### Level 3: End-to-End Testing

- Full workflow tests
- UI interaction testing
- Multi-turn conversations

**Test Coverage**:

- ✅ Setup verification (verify_setup.py)
- ✅ Quick agent test (quick_test_adk.py)
- ✅ Comprehensive tests (test_chefbyte_adk.py)
- ✅ Interactive demo (ChefByte_Demo.ipynb)

## Performance Metrics

- **Average Response Time**: 2-3 seconds
- **Vision Analysis**: 3-5 seconds
- **Recipe Search**: 1-2 seconds (10,000+ recipes)
- **Nutrition Calculation**: <1 second
- **Memory Usage**: ~200MB (agent + tools)

## Deployment

### Local Development

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
echo "GOOGLE_API_KEY=your_key" > .env

# 3. Launch
./launch_ui.sh
```

### Production Deployment (Future)

- Docker containerization
- Cloud deployment (Google Cloud Run)
- Scalable session management
- Multi-user support

## Future Enhancements

### Short Term (1-2 months)

- [ ] Voice input with Hindi/English speech recognition
- [ ] Grocery list generation
- [ ] Shopping cost estimation
- [ ] Meal prep instructions

### Medium Term (3-6 months)

- [ ] User accounts and preferences
- [ ] Recipe rating and feedback
- [ ] Community recipe sharing
- [ ] Integration with grocery delivery APIs

### Long Term (6-12 months)

- [ ] Mobile app (iOS/Android)
- [ ] Augmented reality ingredient scanning
- [ ] Smart fridge integration
- [ ] Personalized health recommendations

## Hackathon Highlights

### What Makes ChefByte Special

1. **Real-World Problem**: Solves actual pain point for Indian households
2. **ADK Showcase**: Demonstrates full ADK capabilities (Agent, Runner, Tools)
3. **Multi-Modal**: Vision + Text (+ Voice coming soon)
4. **Production-Ready**: Complete UI, testing, documentation
5. **Cultural Relevance**: Built FOR Indian users, BY understanding Indian needs

### Technical Achievements

- ✅ Complete ADK implementation with 3 FunctionTools
- ✅ ReAct pattern with intelligent tool selection
- ✅ Session management and conversation continuity
- ✅ Multi-modal input handling
- ✅ Comprehensive testing framework
- ✅ Professional documentation

### Demo Scenarios

1. **Fridge Scanner**: Upload photo → Extract ingredients → Get recipes
2. **Text Query**: "I need high-protein vegetarian recipes" → Smart results
3. **Meal Planning**: Set calories → Get balanced 3-meal plan
4. **Regional Cuisine**: Request Punjabi/South Indian → Authentic recipes
5. **Dietary Filter**: Jain/Halal/Vegan → Compliant suggestions

## Conclusion

ChefByte demonstrates the power of Google ADK for building intelligent, context-aware agents that solve real-world problems. By combining vision analysis, recipe search, and nutrition tracking in a culturally-relevant package, it showcases how AI can be practical, useful, and delightful.

The project is:

- **Complete**: Full implementation from backend to UI
- **Tested**: Comprehensive testing at all levels
- **Documented**: Professional documentation and examples
- **Extensible**: Clean architecture for future enhancements
- **Ready**: Production-ready code and deployment plan

---

**Built with ❤️ for Indian Households**

_ChefByte - Your AI Sous Chef_ 🍳
