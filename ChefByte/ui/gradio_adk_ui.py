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


# Build Gradio Interface
with gr.Blocks(title="ChefByte - AI Meal Planner", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🍳 ChefByte - AI Meal Planning Assistant
    ### Powered by Google ADK & Gemini
    
    Your intelligent companion for Indian household meal planning with vision, recipe search, and nutrition analysis.
    """)
    
    with gr.Tabs():
        
        # Tab 1: Chat Interface
        with gr.Tab("💬 Chat"):
            gr.Markdown("### Chat with ChefByte")
            gr.Markdown("Ask about recipes, ingredients, nutrition, or meal planning")
            
            chatbot = gr.Chatbot(
                value=[],
                label="ChefByte Assistant",
                height=400
            )
            
            msg = gr.Textbox(
                label="Your Message",
                placeholder="E.g., 'I have tomatoes, onions, and rice. What can I cook?'",
                lines=2
            )
            
            with gr.Row():
                submit = gr.Button("Send", variant="primary")
                clear = gr.Button("Clear")
            
            def respond(message, chat_history):
                if not message.strip():
                    return "", chat_history
                
                # Get response
                bot_message = process_text_sync(message, chat_history)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            submit.click(respond, [msg, chatbot], [msg, chatbot])
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: [], None, chatbot)
        
        # Tab 2: Image Upload
        with gr.Tab("📷 Fridge Scanner"):
            gr.Markdown("### Upload a fridge photo to extract ingredients")
            
            with gr.Row():
                with gr.Column():
                    image_input = gr.Image(
                        type="filepath",
                        label="Upload Fridge Photo"
                    )
                    
                    image_query = gr.Textbox(
                        label="Additional Question (Optional)",
                        placeholder="E.g., 'suggest vegetarian recipes'",
                        lines=2
                    )
                    
                    analyze_btn = gr.Button("🔍 Analyze Image", variant="primary")
                
                with gr.Column():
                    image_status = gr.Textbox(
                        label="Status",
                        interactive=False
                    )
                    
                    image_result = gr.Textbox(
                        label="Analysis Result",
                        lines=15,
                        interactive=False
                    )
            
            analyze_btn.click(
                process_image_sync,
                inputs=[image_input, image_query],
                outputs=[image_status, image_result]
            )
        
        # Tab 3: Meal Planner
        with gr.Tab("🍽️ Meal Planner"):
            gr.Markdown("### Plan your meals with specific requirements")
            
            with gr.Row():
                with gr.Column():
                    ingredients_input = gr.Textbox(
                        label="Available Ingredients",
                        placeholder="E.g., tomato, onion, rice, paneer, spinach",
                        lines=3
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
                            "Low Carb"
                        ],
                        label="Dietary Constraints",
                        value="No restrictions"
                    )
                    
                    with gr.Row():
                        calorie_input = gr.Number(
                            label="Calorie Target (optional)",
                            placeholder="E.g., 1800"
                        )
                        
                        meals_input = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=3,
                            step=1,
                            label="Number of Meals"
                        )
                    
                    plan_btn = gr.Button("📋 Create Meal Plan", variant="primary")
                
                with gr.Column():
                    plan_result = gr.Textbox(
                        label="Your Meal Plan",
                        lines=20,
                        interactive=False
                    )
            
            plan_btn.click(
                process_meal_planning_sync,
                inputs=[ingredients_input, dietary_input, calorie_input, meals_input],
                outputs=plan_result
            )
        
        # Tab 4: About
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## About ChefByte
            
            ChefByte is an AI-powered meal planning assistant specifically designed for Indian households.
            
            ### Features:
            - 🔍 **Vision Analysis**: Extract ingredients from fridge photos
            - 🍛 **Recipe Search**: Find recipes matching your ingredients
            - 📊 **Nutrition Tracking**: Calculate calories and macros
            - 🎯 **Meal Planning**: Generate balanced meal plans
            - 🌶️ **Indian Cuisine**: Specialized in Indian recipes and ingredients
            
            ### Technology Stack:
            - **Google ADK**: Agent Development Kit for intelligent orchestration
            - **Gemini 2.5 Flash**: Advanced AI model for vision and text
            - **Multi-modal**: Supports text, images, and voice (coming soon)
            
            ### Dietary Support:
            - Vegetarian, Vegan, Jain, Halal
            - Gluten-free, Dairy-free
            - High-protein, Low-carb
            - Regional preferences (Punjabi, South Indian, Bengali, etc.)
            
            ### How It Works:
            1. Upload a fridge photo or list ingredients
            2. Specify dietary constraints and calorie targets
            3. ChefByte analyzes and suggests recipes
            4. Get a complete meal plan with nutrition info
            
            ---
            
            **Built for Google ADK Hackathon 2025**
            
            Optimized for Indian households with support for Hindi/English ingredient names
            and regional recipe preferences.
            """)
    
    gr.Markdown("""
    ---
    <center>
    Made with ❤️ using Google ADK | ChefByte © 2025
    </center>
    """)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🍳 Starting ChefByte Gradio UI")
    print("="*60)
    print("\nAgent initialized with tools:")
    print(f"  - Vision Tool: Extract ingredients from images")
    print(f"  - Recipe Search: Find matching recipes")
    print(f"  - Nutrition Estimator: Calculate nutrition")
    print("\nLaunching web interface...")
    print("="*60 + "\n")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True  # Creates a public shareable link
    )
