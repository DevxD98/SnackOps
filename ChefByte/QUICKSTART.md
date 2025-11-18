# ChefByte Quick Reference

## Initial Setup

```bash
# Run the automated setup
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Activate Virtual Environment

**Always run this before using ChefByte:**

```bash
source venv/bin/activate
```

You'll know it's activated when you see `(venv)` or `Py ChefByte` in your terminal prompt.

## Deactivate Virtual Environment

```bash
deactivate
```

## Run the Application

### Web UI (Gradio)

```bash
source venv/bin/activate
python ui/gradio_ui.py
```

### Jupyter Notebook

```bash
source venv/bin/activate
jupyter notebook notebook/ChefByte_Demo.ipynb
```

### Python Script

```bash
source venv/bin/activate
python agent/orchestrator.py
```

## Environment Variables

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

## Testing Individual Tools

```bash
source venv/bin/activate

# Test vision tool
python agent/tools/vision_tool.py

# Test ingredient normalizer
python agent/tools/ingredient_normalizer.py

# Test recipe search
python agent/tools/recipe_search.py

# Test nutrition estimator
python agent/tools/nutrition_estimator.py
```

## Troubleshooting

### Error: "externally-managed-environment"

**Solution:** Make sure you're using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Error: "No module named 'agent'"

**Solution:** Make sure you're running from the PantryPilot directory:

```bash
cd /Users/devmondal/SnackOps/PantryPilot
source venv/bin/activate
```

### Error: "GEMINI_API_KEY not found"

**Solution:** Create and configure your `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

## Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## Clean Installation

```bash
# Remove virtual environment
rm -rf venv

# Recreate it
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
