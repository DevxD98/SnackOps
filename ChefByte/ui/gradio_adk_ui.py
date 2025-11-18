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


async def process_image_upload(image_path: str, query: Optional[str] = None) -> Tuple[str, str]:
    """
    Process uploaded image through vision tool
    
    Args:
        image_path: Path to uploaded image
        query: Optional text query about the image
    
    Returns:
        Tuple of (ingredients_text, agent_response)
    """
    global current_session_id
    
    if not image_path:
        return "No image uploaded", ""
    
    # Create query for vision analysis
    if query:
        full_query = f"Analyze this fridge image and {query}. Image: {image_path}"
    else:
        full_query = f"Analyze this fridge photo and extract all ingredients. Then suggest recipes I can make. Image: {image_path}"
    
    # Run agent with image
    result = await agent.run_async(full_query, session_id=current_session_id)
    
    if result['success']:
        return "Image analyzed successfully!", result['response']
    else:
        return f"Error: {result.get('error')}", ""


def process_image_sync(image_path: str, query: Optional[str] = None) -> Tuple[str, str]:
    """Synchronous wrapper for image processing"""
    return run_async_safe(process_image_upload(image_path, query))


async def process_meal_planning(
    ingredients: str,
    dietary: str,
    calories: Optional[int],
    meals: int
) -> str:
    """
    Process structured meal planning request
    
    Args:
        ingredients: Comma-separated ingredients
        dietary: Dietary constraints
        calories: Target calories
        meals: Number of meals
    
    Returns:
        Meal plan response
    """
    global current_session_id
    
    # Build query
    query = f"""Create a meal plan with:
- Ingredients: {ingredients}
- Dietary: {dietary if dietary else 'No restrictions'}
- Calorie target: {calories if calories else 'No target'}
- Number of meals: {meals}

Please provide recipes with nutrition information."""
    
    result = await agent.run_async(query, session_id=current_session_id)
    
    if result['success']:
        return result['response']
    else:
        return f"❌ Error: {result.get('error')}"


def process_meal_planning_sync(ingredients: str, dietary: str, calories: Optional[int], meals: int) -> str:
    """Synchronous wrapper for meal planning"""
    return run_async_safe(process_meal_planning(ingredients, dietary, calories, meals))


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
        .gradio-container {max-width: 1200px !important;}
        h1 {font-size: 2.5rem; font-weight: 700; color: #1F2937; margin-bottom: 0.5rem;}
        h2 {font-size: 1.5rem; font-weight: 600; color: #374151; margin-bottom: 1rem;}
        h3 {font-size: 1.25rem; font-weight: 600; color: #4B5563;}
        .contain {border-radius: 12px;}
        .tabitem {padding: 2rem;}
        footer {display: none !important;}
    """
) as demo:
    
    # Header
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("""
            # ChefByte
            ### AI-Powered Meal Planning Assistant
            
            Intelligent companion for Indian household meal planning with vision analysis, recipe search, and nutrition tracking.
            """)
    
    gr.Markdown("---")
    
    with gr.Tabs():
        
        # Tab 1: Conversational Chat
        with gr.Tab("Chat Assistant"):
            with gr.Row():
                gr.Markdown("""
                ### Conversational Meal Planning
                Ask about recipes, ingredients, nutrition information, or get personalized meal suggestions.
                """)
            
            chatbot = gr.Chatbot(
                value=[],
                label="",
                height=500,
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
            
            submit.click(respond, [msg, chatbot], [msg, chatbot])
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
        
        # Tab 2: Vision Scanner
        with gr.Tab("Fridge Scanner"):
            with gr.Row():
                gr.Markdown("""
                ### Visual Ingredient Detection
                Upload a photo of your fridge or pantry to automatically extract ingredients using AI vision.
                """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(
                        type="filepath",
                        label="Upload Photo",
                        height=350,
                        sources=["upload", "webcam"]
                    )
                    
                    image_query = gr.Textbox(
                        label="Additional Instructions (Optional)",
                        placeholder="e.g., 'suggest vegetarian recipes' or 'focus on quick meals'",
                        lines=2
                    )
                    
                    analyze_btn = gr.Button("Analyze Image", variant="primary", size="lg")
                    
                    gr.Examples(
                        examples=[
                            ["Show me quick recipes I can make"],
                            ["Suggest vegetarian Indian dishes"],
                            ["What healthy meals can I prepare?"]
                        ],
                        inputs=image_query,
                        label="Example questions"
                    )
                
                with gr.Column(scale=1):
                    image_status = gr.Textbox(
                        label="Detection Status",
                        interactive=False,
                        lines=1
                    )
                    
                    image_result = gr.Textbox(
                        label="Ingredients & Recipe Suggestions",
                        lines=17,
                        interactive=False,
                        show_copy_button=True
                    )
            
            analyze_btn.click(
                process_image_sync,
                inputs=[image_input, image_query],
                outputs=[image_status, image_result]
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
                    
                    ingredients_input = gr.Textbox(
                        label="Available Ingredients",
                        placeholder="Enter ingredients separated by commas (e.g., tomato, onion, rice, chicken, spinach)",
                        lines=4
                    )
                    
                    dietary_input = gr.Dropdown(
                        choices=[
                            "No restrictions",
                            "Vegetarian",
                            "Vegan", 
                            "Gluten-free",
                            "Jain",
                            "Halal",
                            "High Protein",
                            "Low Carb",
                            "Keto",
                            "Paleo"
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
                inputs=[ingredients_input, dietary_input, calorie_input, meals_input],
                outputs=plan_result
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
                    
                    **Built for Google ADK Hackathon 2025**  
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
