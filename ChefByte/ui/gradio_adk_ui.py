import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import asyncio
from typing import Optional, Tuple, List
from adk_agent import ChefByteADKAgent
from concurrent.futures import ThreadPoolExecutor
import threading


# Initialize agent
print("Initializing ChefByte ADK Agent...")
agent = ChefByteADKAgent()
print("Agent ready!")

# Session management
current_session_id = "default_user"

# Thread-local storage for event loops
thread_local = threading.local()


def get_or_create_event_loop():
    """Get or create an event loop for the current thread"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def run_async_safe(coro):
    """Safely run async coroutine in current thread"""
    loop = get_or_create_event_loop()
    return loop.run_until_complete(coro)


async def process_text_message(message: str, history: List) -> str:
    """
    Process text message through ADK agent
    
    Args:
        message: User's text input
        history: Chat history
    
    Returns:
        Agent's response
    """
    global current_session_id
    
    # Run agent
    result = await agent.run_async(message, session_id=current_session_id)
    
    if result['success']:
        return result['response']
    else:
        return f"❌ Error: {result.get('error', 'Unknown error')}"


def process_text_sync(message: str, history: List) -> str:
    """Synchronous wrapper for Gradio"""
    return run_async_safe(process_text_message(message, history))


async def extract_ingredients_from_image(image_path: str) -> Tuple[str, str, List[str]]:
    """
    Extract ingredients from image and return as list
    
    Args:
        image_path: Path to uploaded image
    
    Returns:
        Tuple of (status_message, agent_message, ingredients_list)
    """
    global current_session_id
    
    if not image_path:
        return "No image uploaded", "", []
    
    # Query for structured ingredient extraction
    full_query = f"""Analyze this fridge/pantry photo and extract ONLY the ingredient names as a simple list.

Rules:
- List each ingredient on a new line
- Use simple, common names (e.g., "Eggs" not "Unidentified white powder/granules")
- Avoid descriptions or parentheses
- Be specific but concise (e.g., "Butter" not "Packaged Food (e.g., Butter, Cheese)")

Image: {image_path}"""
    
    # Run agent with image
    result = await agent.run_async(full_query, session_id=current_session_id)
    
    if result['success']:
        # Parse ingredients from response
        response_text = result['response']
        
        # Extract clean ingredient names
        ingredients = []
        for line in response_text.split('\n'):
            line = line.strip()
            # Skip headers, empty lines, and explanatory text
            if not line or line.startswith('#') or line.startswith('*') or line.lower().startswith('based on'):
                continue
            
            # Remove bullet points, dashes, numbers, asterisks
            clean = line.lstrip('•-*0123456789. ').strip()
            
            # Skip if too long (likely a sentence) or too short
            if clean and 2 < len(clean) < 30:
                # Remove content in parentheses
                if '(' in clean:
                    clean = clean.split('(')[0].strip()
                # Skip if contains common non-ingredient phrases
                skip_phrases = ['see', 'following', 'based on', 'photo', 'image', 'fridge', 'ingredients']
                if not any(phrase in clean.lower() for phrase in skip_phrases):
                    ingredients.append(clean.title())
        
        # Deduplicate and sort
        ingredients = sorted(list(set(ingredients)))
        
        return f"✅ Detected {len(ingredients)} ingredients!", response_text, ingredients
    else:
        return f"❌ Error: {result.get('error')}", "", []


def extract_ingredients_sync(image_path: str) -> Tuple[str, str, gr.update, gr.update, gr.update]:
    """Synchronous wrapper for ingredient extraction"""
    status, message, ingredients = run_async_safe(extract_ingredients_from_image(image_path))
    
    # Return status, agent message, and CheckboxGroup updates for scanner, chat, and meal planner
    return status, message, gr.update(choices=ingredients, value=ingredients), gr.update(choices=ingredients, value=ingredients), gr.update(choices=ingredients, value=ingredients)


async def generate_recipes_from_ingredients(selected_ingredients: List[str], dietary: str, cuisine: str, chat_history: List) -> Tuple[str, List, gr.update]:
    """
    Generate recipes from selected ingredients and redirect to chat
    
    Args:
        selected_ingredients: List of selected ingredient names
        dietary: Dietary constraints
        cuisine: Cuisine preference
        chat_history: Current chat history
    
    Returns:
        Tuple of (confirmation_message, updated_chat_history, tab_update)
    """
    global current_session_id
    
    if not selected_ingredients:
        return "⚠️ Please select at least one ingredient!", chat_history, gr.update()
    
    # Build query
    ingredients_str = ", ".join(selected_ingredients)
    user_query = f"I have scanned my fridge and have these ingredients: {ingredients_str}."
    
    if dietary:
        user_query += f"\nDietary preference: {dietary}."
    if cuisine:
        user_query += f"\nCuisine preference: {cuisine}."
    
    user_query += "\n\nPlease show me the top 3 recipes I can make using the beautiful template format."
    
    # Get agent response
    result = await agent.run_async(user_query, session_id=current_session_id)
    
    # Add to chat history
    if result['success']:
        bot_message = result['response']
    else:
        bot_message = f"❌ Error: {result.get('error')}"
    
    # Update chat history
    new_history = chat_history + [(user_query, bot_message)]
    
    # Return confirmation, updated chat, and tab switch to Chat Assistant (index 0)
    return f"✅ Redirecting to Chat Assistant with {len(selected_ingredients)} ingredients...", new_history, gr.update(selected=0)


def generate_recipes_sync(selected_ingredients: List[str], dietary: str, cuisine: str, chat_history: List) -> Tuple[str, List, gr.update]:
    """Synchronous wrapper for recipe generation"""
    return run_async_safe(generate_recipes_from_ingredients(selected_ingredients, dietary, cuisine, chat_history))


def add_manual_ingredient(current_choices: List[str], current_values: List[str], new_ingredient: str) -> Tuple[gr.update, gr.update, str]:
    """
    Add a manually entered ingredient to the list
    
    Args:
        current_choices: Current ingredient choices
        current_values: Currently selected ingredients
        new_ingredient: New ingredient to add
    
    Returns:
        Tuple of (updated_choices, updated_values, cleared_textbox)
    """
    if not new_ingredient or not new_ingredient.strip():
        return gr.update(), gr.update(), ""
    
    clean_ingredient = new_ingredient.strip().title()
    
    # Add to choices if not already there
    updated_choices = list(current_choices) if current_choices else []
    if clean_ingredient not in updated_choices:
        updated_choices.append(clean_ingredient)
        updated_choices.sort()
    
    # Add to selected values
    updated_values = list(current_values) if current_values else []
    if clean_ingredient not in updated_values:
        updated_values.append(clean_ingredient)
    
    return gr.update(choices=updated_choices, value=updated_values), gr.update(value=updated_values), ""


def add_ingredients_to_message(selected_ingredients: List[str], current_message: str, dietary: str, cuisine: str) -> str:
    """Add selected ingredients to the message textbox"""
    if not selected_ingredients:
        return current_message
    
    ingredients_text = ", ".join(selected_ingredients)
    new_message = f"I have these ingredients: {ingredients_text}."
    
    if dietary:
        new_message += f" Dietary preference: {dietary}."
    if cuisine:
        new_message += f" Cuisine: {cuisine}."
    
    new_message += " What recipes can I make?"
    
    return new_message


def quick_recipe_request(selected_ingredients: List[str], dietary: str, cuisine: str, chat_history: List) -> Tuple[str, List]:
    """Quick recipe generation from sidebar"""
    if not selected_ingredients:
        return "", chat_history
    
    # Build query
    ingredients_str = ", ".join(selected_ingredients)
    user_query = f"I have these ingredients: {ingredients_str}."
    
    if dietary:
        user_query += f" Dietary preference: {dietary}."
    if cuisine:
        user_query += f" Cuisine: {cuisine}."
    
    user_query += " Please show me the top 3 recipes I can make using the beautiful template format."
    
    # Get response
    result = run_async_safe(agent.run_async(user_query, session_id=current_session_id))
    
    if result['success']:
        bot_message = result['response']
    else:
        bot_message = f"❌ Error: {result.get('error')}"
    
    new_history = chat_history + [(user_query, bot_message)]
    
    return "", new_history


async def process_meal_planning(
    selected_ingredients: List[str],
    manual_ingredients: str,
    dietary: str,
    calories: Optional[int],
    meals: int
) -> str:
    """
    Process structured meal planning request
    
    Args:
        selected_ingredients: List of selected ingredients from checkboxes
        manual_ingredients: Manually entered comma-separated ingredients
        dietary: Dietary constraints
        calories: Target calories
        meals: Number of meals
    
    Returns:
        Meal plan response
    """
    global current_session_id
    
    # Combine selected and manual ingredients
    all_ingredients = []
    if selected_ingredients:
        all_ingredients.extend(selected_ingredients)
    if manual_ingredients:
        manual_list = [i.strip() for i in manual_ingredients.split(',') if i.strip()]
        all_ingredients.extend(manual_list)
    
    # Remove duplicates and join
    ingredients_str = ", ".join(list(set(all_ingredients))) if all_ingredients else "No specific ingredients"
    
    # Build query
    query = f"""Create a meal plan with:
- Ingredients: {ingredients_str}
- Dietary: {dietary if dietary else 'No restrictions'}
- Calorie target: {calories if calories else 'No target'}
- Number of meals: {meals}

Please provide recipes with nutrition information."""
    
    result = await agent.run_async(query, session_id=current_session_id)
    
    if result['success']:
        return result['response']
    else:
        return f"❌ Error: {result.get('error')}"


def process_meal_planning_sync(selected_ingredients: List[str], manual_ingredients: str, dietary: str, calories: Optional[int], meals: int) -> str:
    """Synchronous wrapper for meal planning"""
    return run_async_safe(process_meal_planning(selected_ingredients, manual_ingredients, dietary, calories, meals))


# Build Professional Gradio Interface with Custom Theme
custom_theme = gr.themes.Soft(
    primary_hue="emerald",
    secondary_hue="amber",
    neutral_hue="slate"
).set(
    body_background_fill="#FAFAFA",
    block_title_text_weight="600",
    block_border_width="1px",
    block_shadow="0 1px 3px 0 rgb(0 0 0 / 0.1)",
    button_primary_background_fill="#10B981",
    button_primary_background_fill_hover="#059669",
    button_primary_text_color="white",
    input_border_color="#E2E8F0",
    input_shadow="0 1px 2px 0 rgb(0 0 0 / 0.05)",
)

with gr.Blocks(
    title="ChefByte - AI Meal Planner", 
    theme=custom_theme,
    css="""
        .gradio-container {max-width: 100% !important; padding: 1rem 2rem;}
        h1 {font-size: 2.5rem; font-weight: 700; color: #4B5563 !important; margin-bottom: 0.5rem;}
        h2 {font-size: 1.5rem; font-weight: 600; color: #1F2937 !important; margin-bottom: 1rem;}
        h3 {font-size: 1.25rem; font-weight: 600; color: #374151 !important;}
        .markdown p {color: #1F2937 !important;}
        .contain {border-radius: 12px;}
        .tabitem {padding: 1.5rem;}
        footer {display: none !important;}
        .ingredient-chip {background: #10B981; color: white; padding: 4px 12px; border-radius: 16px; margin: 2px; display: inline-block;}
    """
) as demo:
    
    # Header
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            <h1 style="color: #ffffff; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;">ChefByte</h1>
            <h3 style="color: #059669; font-weight: 600; font-size: 1.25rem; margin-bottom: 0.75rem;">AI-Powered Meal Planning Assistant</h3>
            <p style="color: #ffffff; font-size: 1rem; line-height: 1.5;">Intelligent companion for Indian household meal planning with vision analysis, recipe search, and nutrition tracking.</p>
            """)
    
    gr.Markdown("---")
    
    with gr.Tabs() as tabs:
        
        # Tab 1: Conversational Chat
        with gr.Tab("Chat Assistant"):
            with gr.Row():
                # Main chat area
                with gr.Column(scale=7):
                    gr.Markdown("""
                    ### 💬 Conversational Meal Planning
                    Ask about recipes, ingredients, nutrition information, or get personalized meal suggestions.
                    """)
                    
                    chatbot = gr.Chatbot(
                        value=[],
                        label="",
                        height=550,
                        show_label=False,
                        avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=ChefByte"),
                        bubble_full_width=False
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="",
                            placeholder="Ask me anything... e.g., 'I have tomatoes, onions, and rice. What can I cook?'",
                            lines=2,
                            scale=9,
                            show_label=False
                        )
                        with gr.Column(scale=1, min_width=100):
                            submit = gr.Button("Send", variant="primary", size="lg")
                    
                    with gr.Row():
                        clear = gr.ClearButton([msg, chatbot], value="Clear Conversation", size="sm")
                
                # Ingredient sidebar
                with gr.Column(scale=3):
                    gr.Markdown("""
                    ### 🥕 My Ingredients
                    *Select ingredients to add to your message*
                    """)
                    
                    chat_ingredient_selector = gr.CheckboxGroup(
                        choices=[],
                        value=[],
                        label="",
                        interactive=True,
                        show_label=False
                    )
                    
                    with gr.Row():
                        add_to_msg_btn = gr.Button("➕ Add Selected to Message", size="sm", variant="secondary")
                    
                    gr.Markdown("---")
                    
                    gr.Markdown("""
                    ### ⚙️ Quick Filters
                    """)
                    
                    chat_dietary = gr.Dropdown(
                        choices=["", "Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free", "Jain"],
                        label="Dietary Preference",
                        value=""
                    )
                    
                    chat_cuisine = gr.Dropdown(
                        choices=["", "Indian", "Punjabi", "South Indian", "Bengali", "International"],
                        label="Cuisine Type",
                        value="Indian"
                    )
                    
                    quick_recipe_btn = gr.Button("🚀 Get Recipe Suggestions", variant="primary", size="sm")
                
            gr.Examples(
                examples=[
                    "I have tomatoes, onions, and rice. What can I cook?",
                    "Suggest me 3 vegetarian Indian recipes",
                    "Create a 1800 calorie meal plan for today",
                    "What are the nutrition facts of Paneer Tikka Masala?"
                ],
                inputs=msg,
                label="Try these examples"
            )
            
            def respond(message, chat_history):
                if not message.strip():
                    return "", chat_history
                
                # Get response
                bot_message = process_text_sync(message, chat_history)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            # Chat message handlers
            submit.click(respond, [msg, chatbot], [msg, chatbot])
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            
            # Add ingredients to message button
            add_to_msg_btn.click(
                add_ingredients_to_message,
                inputs=[chat_ingredient_selector, msg, chat_dietary, chat_cuisine],
                outputs=[msg]
            )
            
            # Quick recipe button
            quick_recipe_btn.click(
                quick_recipe_request,
                inputs=[chat_ingredient_selector, chat_dietary, chat_cuisine, chatbot],
                outputs=[msg, chatbot]
            )
        
        # Tab 2: Vision Scanner
        with gr.Tab("Fridge Scanner"):
            with gr.Row():
                gr.Markdown("""
                ### Visual Ingredient Detection
                Upload a photo of your fridge or pantry to automatically extract ingredients, then select which ones to use for recipes.
                """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(
                        type="filepath",
                        label="📸 Upload Fridge/Pantry Photo",
                        height=300,
                        sources=["upload", "webcam"]
                    )
                    
                    scan_btn = gr.Button("🔍 Scan for Ingredients", variant="primary", size="lg")
                    
                    scan_status = gr.Textbox(
                        label="Scan Status",
                        interactive=False,
                        lines=1
                    )
                    
                    # Agent message box
                    agent_message = gr.Textbox(
                        label="Agent Response",
                        interactive=False,
                        lines=4,
                        show_copy_button=True
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🥕 Detected Ingredients")
                    gr.Markdown("*Select/deselect ingredients you want to use*")
                    
                    ingredient_selector = gr.CheckboxGroup(
                        choices=[],
                        value=[],
                        label="",
                        interactive=True,
                        show_label=False
                    )
                    
                    # Manual ingredient add/remove
                    with gr.Row():
                        manual_ingredient = gr.Textbox(
                            placeholder="Add ingredient manually (e.g., 'tomatoes')",
                            label="",
                            show_label=False,
                            scale=3
                        )
                        add_ingredient_btn = gr.Button("➕ Add", size="sm", scale=1)
                    
                    with gr.Row():
                        dietary_filter = gr.Dropdown(
                            choices=["", "Vegetarian", "Non-Vegetarian", "Vegan", "Gluten-Free", "Jain"],
                            label="Dietary Preference",
                            value=""
                        )
                        cuisine_filter = gr.Dropdown(
                            choices=["", "Indian", "Punjabi", "South Indian", "Bengali", "International"],
                            label="Cuisine Type",
                            value="Indian"
                        )
                    
                    generate_btn = gr.Button("✨ Generate Recipes", variant="primary", size="lg")
            
            with gr.Row():
                recipe_output = gr.Markdown(
                    label="Recipe Suggestions",
                    value="*Scan your fridge and select ingredients to get started!*"
                )
            
                # Scan button will be connected after all tabs are defined

            # Connect manual ingredient add button
            add_ingredient_btn.click(
                add_manual_ingredient,
                inputs=[ingredient_selector, ingredient_selector, manual_ingredient],
                outputs=[ingredient_selector, ingredient_selector, manual_ingredient]
            )
            
            # Also allow pressing Enter to add ingredient
            manual_ingredient.submit(
                add_manual_ingredient,
                inputs=[ingredient_selector, ingredient_selector, manual_ingredient],
                outputs=[ingredient_selector, ingredient_selector, manual_ingredient]
            )
            
            # Connect generate button - redirect to chat with context
            generate_btn.click(
                generate_recipes_sync,
                inputs=[ingredient_selector, dietary_filter, cuisine_filter, chatbot],
                outputs=[recipe_output, chatbot, tabs]
            )
        
        # Tab 3: Structured Meal Planner
        with gr.Tab("Meal Planner"):
            with gr.Row():
                gr.Markdown("""
                ### Custom Meal Plan Generator
                Create personalized meal plans based on your ingredients, dietary preferences, and nutrition goals.
                """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### Ingredients & Preferences")
                    
                    # Ingredient selector for meal planner
                    gr.Markdown("**Available Ingredients**")
                    planner_ingredient_selector = gr.CheckboxGroup(
                        choices=[],
                        value=[],
                        label="",
                        interactive=True,
                        show_label=False
                    )
                    
                    # Manual ingredient input as backup
                    with gr.Accordion("Or enter manually", open=False):
                        ingredients_input = gr.Textbox(
                            label="",
                            placeholder="Enter ingredients separated by commas (e.g., tomato, onion, rice)",
                            lines=3,
                            show_label=False
                        )
                    
                    dietary_input = gr.Dropdown(
                        choices=[
                            "No restrictions",
                            "Vegetarian",
                            "Non-Vegetarian",
                            "Vegan", 
                            "Gluten-free",
                            "Jain",
                            "High Protein",
                            "Low Carb",
                            "Keto"
                        ],
                        label="Dietary Constraints",
                        value="No restrictions"
                    )
                    
                    gr.Markdown("#### Nutrition Goals")
                    
                    with gr.Row():
                        calorie_input = gr.Number(
                            label="Daily Calorie Target",
                            placeholder="e.g., 1800",
                            minimum=800,
                            maximum=4000,
                            step=50
                        )
                        
                        meals_input = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=3,
                            step=1,
                            label="Number of Meals"
                        )
                    
                    plan_btn = gr.Button("Generate Meal Plan", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    gr.Markdown("#### Your Personalized Meal Plan")
                    
                    plan_result = gr.Textbox(
                        label="",
                        lines=22,
                        interactive=False,
                        show_copy_button=True,
                        show_label=False
                    )
            
            plan_btn.click(
                process_meal_planning_sync,
                inputs=[planner_ingredient_selector, ingredients_input, dietary_input, calorie_input, meals_input],
                outputs=plan_result
            )
        
        # Connect scan button after all components are defined
        scan_btn.click(
            extract_ingredients_sync,
            inputs=[image_input],
            outputs=[scan_status, agent_message, ingredient_selector, chat_ingredient_selector, planner_ingredient_selector]
        )
        
        # Tab 4: Information & Features
        with gr.Tab("About"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ## About ChefByte
                    
                    ChefByte is an intelligent meal planning assistant powered by Google's Agent Development Kit (ADK) 
                    and Gemini AI, specifically optimized for Indian households.
                    
                    ### Core Capabilities
                    
                    **Vision Analysis**  
                    Extract ingredients from photos using advanced computer vision
                    
                    **Recipe Discovery**  
                    Search through 6,800+ Indian and international recipes
                    
                    **Nutrition Tracking**  
                    Calculate calories, protein, carbs, and fats for meal planning
                    
                    **Smart Planning**  
                    Generate balanced meal plans based on your goals
                    
                    **Cultural Context**  
                    Specialized in Indian cuisine with regional variations
                    """)
                
                with gr.Column():
                    gr.Markdown("""
                    ### Technology Stack
                    
                    - **Google ADK 1.18.0** - Agent orchestration framework
                    - **Gemini 2.5 Flash** - Multi-modal AI model
                    - **Python 3.12** - Modern Python with type safety
                    - **Gradio 5.0** - Interactive web interface
                    
                    ### Supported Diets
                    
                    Vegetarian • Vegan • Jain • Halal • Gluten-free • Keto • Paleo • High-Protein • Low-Carb
                    
                    ### Regional Cuisines
                    
                    Punjabi • South Indian • Bengali • Gujarati • Maharashtrian • Andhra • Continental • Italian • Mexican
                    
                    ### How It Works
                    
                    1. **Input** - Provide ingredients via text, photo, or voice
                    2. **Analysis** - AI extracts and understands your ingredients
                    3. **Search** - Matches against 6,800+ recipe database
                    4. **Plan** - Creates optimized meal combinations
                    5. **Nutrition** - Calculates complete nutritional breakdown
                    
                    ---
                    
                    **Built for Agents Intensive - Capstone Project • 2025**  
                    Optimized for Indian households • Multi-lingual support • Persistent memory
                    """)
    
    # Footer
    gr.Markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0; color: #64748b; border-top: 1px solid #e2e8f0; margin-top: 2rem;">
        <p style="margin: 0; font-size: 0.875rem;">ChefByte © 2025 • Powered by Google ADK & Gemini</p>
    </div>
    """)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ChefByte - AI-Powered Meal Planning Assistant")
    print("="*70)
    print("\n  Initializing Components:")
    print("    ✓ Vision Tool - Extract ingredients from images")
    print("    ✓ Recipe Search - 6,889 Indian & international recipes")
    print("    ✓ Nutrition Estimator - Calculate calories & macros")
    print("    ✓ Persistent Memory - User preferences & history")
    print("\n  Technology Stack:")
    print("    • Google ADK 1.18.0")
    print("    • Gemini 2.5 Flash")
    print("    • Python 3.12.9")
    print("    • Gradio 5.49.1")
    print("\n  Launching web interface...")
    print("="*70 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Creates a public shareable link
        show_api=False
    )
