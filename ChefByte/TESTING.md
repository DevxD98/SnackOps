# Testing ChefByte ADK Agent

## Quick Start

### 1. **Super Quick Test** (Recommended First)

Just run one simple query to verify everything works:

```bash
cd /Users/devmondal/SnackOps/ChefByte
venv/bin/python quick_test_adk.py
```

This will:

- Initialize the ADK agent
- Send a simple ingredient query
- Show you the response
- Takes ~10-30 seconds

---

### 2. **Full Test Suite**

Run comprehensive tests covering all features:

```bash
venv/bin/python test_chefbyte_adk.py
```

This runs 7 different tests:

1. ✅ Basic greeting and introduction
2. ✅ Ingredient-based recipe suggestions
3. ✅ Dietary constraints handling
4. ✅ Indian cuisine knowledge (spice translations)
5. ✅ Full meal planning with calorie targets
6. ✅ Multi-turn conversation continuity
7. ✅ Synchronous wrapper functionality

Expected time: ~2-5 minutes

---

### 3. **Interactive Testing**

For manual testing, you can use Python REPL:

```bash
venv/bin/python
```

Then:

```python
from adk_agent import ChefByteADKAgent

# Create agent
agent = ChefByteADKAgent()

# Test a query (sync)
result = agent.run("What can I make with paneer and spinach?")
print(result['response'])

# Or async
import asyncio
result = asyncio.run(agent.run_async("Plan a 1800 calorie vegetarian day"))
print(result['response'])
```

---

## What to Expect

### ✅ Success Looks Like:

```
✓ ChefByte ADK Agent initialized with 1 tools
✓ Created ADK Agent: ChefByte
✓ Created Runner

Response:
Hello! I'm ChefByte, your AI meal planning assistant...
[Agent provides helpful response]
```

### ❌ Common Issues:

**1. Missing API Key**

```
Error: API key not found
```

**Fix:** Make sure `.env` file exists with `GOOGLE_API_KEY=your_key`

**2. Import Errors**

```
ModuleNotFoundError: No module named 'google.adk'
```

**Fix:** Install dependencies:

```bash
venv/bin/pip install -r requirements.txt
```

**3. Timeout/Hanging**

- ADK may take 10-30 seconds for first response (model loading)
- Be patient, especially on first run
- If it hangs >60s, press Ctrl+C and try again

---

## Testing Individual Tools

### Vision Tool (Ingredient Extraction)

```python
from adk_agent.tools import extract_ingredients_from_image

# Test with an image
result = extract_ingredients_from_image("path/to/fridge_photo.jpg")
print(result)
```

### Direct ADK Agent Call

```python
from adk_agent import ChefByteADKAgent

agent = ChefByteADKAgent()

# Simple query
result = agent.run("Hello!")
print(result['response'])

# With session continuity
result1 = agent.run("I have chicken and rice", session_id="my_session")
result2 = agent.run("Make it vegetarian", session_id="my_session")
# The agent remembers the context!
```

---

## Expected Agent Capabilities

The agent should be able to:

✅ **Understand Indian Ingredients**

- Recognize Hindi names (haldi=turmeric, dhania=coriander)
- Know regional dishes (Palak Paneer, Biryani, Sambar)

✅ **Meal Planning**

- Suggest recipes based on available ingredients
- Calculate nutrition and calories
- Plan meals meeting dietary constraints

✅ **Dietary Awareness**

- Vegetarian, vegan, Jain, halal options
- High-protein, low-carb variations
- Allergy considerations

✅ **Multi-turn Conversations**

- Remember context across messages (with same session_id)
- Refine suggestions based on follow-ups

---

## Next Steps After Testing

Once basic tests pass:

1. **Add More Tools** - Convert recipe_search and nutrition_estimator
2. **Build UI** - Integrate with Gradio for web interface
3. **Add Vision** - Test with actual fridge photos
4. **Voice Input** - Add speech-to-text for Hindi/English
5. **Deploy** - Package for hackathon submission

---

## Troubleshooting

### Agent responds but ignores tools

- Check that tools are registered: `print(agent.agent.tools)`
- Tools must be FunctionTool instances with proper docstrings

### Responses are generic

- ADK is working but tools aren't being called
- System prompt might need tuning
- Check `adk_agent/prompts/system_prompt.md`

### Memory issues

- Each session_id maintains separate conversation history
- Use same session_id for continuity
- Clear sessions: `agent.session_service.delete_session(session_id)`

---

## Quick Debug Commands

```bash
# Check ADK version
venv/bin/python -c "import google.adk; print(google.adk.__version__)"

# List installed tools
venv/bin/python -c "from adk_agent import ChefByteADKAgent; a = ChefByteADKAgent(); print([t.name for t in a.agent.tools])"

# Verify Gemini API
venv/bin/python -c "from gemini_setup import get_gemini_model; m = get_gemini_model(); print('API working')"
```

---

Happy Testing! 🍳🤖
