"""
Gradio UI for ChefByte
Interactive web interface for the meal planning agent
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
from agent.orchestrator import ChefByteAgent


def create_meal_plan(fridge_image, receipt_image, dietary_constraints, calorie_target, meal_count):
    """
    Generate meal plan from user inputs
    
    Args:
        fridge_image: Uploaded fridge photo
        receipt_image: Uploaded receipt photo (optional)
        dietary_constraints: Selected dietary constraints
        calorie_target: Target daily calories
        meal_count: Number of meals
    
    Returns:
        Formatted meal plan text
    """
    try:
        # Initialize agent
        agent = ChefByteAgent()
        
        # Convert inputs
        constraints_list = dietary_constraints if dietary_constraints else []
        calorie_int = int(calorie_target) if calorie_target else None
        meal_count_int = int(meal_count)
        
        # Get image paths
        fridge_path = fridge_image if fridge_image else None
        receipt_path = receipt_image if receipt_image else None
        
        # Generate meal plan
        result = agent.run(
            fridge_image=fridge_path,
            receipt_image=receipt_path,
            dietary_constraints=constraints_list,
            calorie_target=calorie_int,
            meal_count=meal_count_int
        )
        
        # Format output
        output = "# 🍽️ Your ChefByte Meal Plan\n\n"
        output += "---\n\n"
        output += result['meal_plan']
        output += "\n\n---\n\n"
        output += "## 📊 Summary\n\n"
        output += f"- **Recipes Considered**: {result['recipes_considered']}\n"
        output += f"- **Tools Used**: {', '.join(result['tool_history'])}\n"
        
        if result['nutrition_summary'].get('total_nutrition'):
            output += "\n### Total Daily Nutrition:\n"
            for key, value in result['nutrition_summary']['total_nutrition'].items():
                output += f"- **{key}**: {value}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error generating meal plan: {str(e)}\n\nPlease check your inputs and try again."


def create_ui():
    """
    Create the Gradio interface
    
    Returns:
        Gradio Blocks app
    """
    with gr.Blocks(title="ChefByte 🍳", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🍳 ChefByte - AI Meal Planning Agent
            
            Upload photos of your fridge and receipts, set your dietary preferences, 
            and let AI plan your meals!
            
            Powered by Google Gemini Pro + Gemini Vision
            """
        )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📸 Upload Images")
                
                fridge_image = gr.Image(
                    label="Fridge Photo",
                    type="filepath",
                    sources=["upload"]
                )
                
                receipt_image = gr.Image(
                    label="Receipt Photo (Optional)",
                    type="filepath",
                    sources=["upload"]
                )
                
                gr.Markdown("### ⚙️ Preferences")
                
                dietary_constraints = gr.CheckboxGroup(
                    label="Dietary Constraints",
                    choices=[
                        "vegetarian",
                        "vegan",
                        "gluten-free",
                        "dairy-free",
                        "low-carb",
                        "high-protein"
                    ]
                )
                
                calorie_target = gr.Number(
                    label="Daily Calorie Target (Optional)",
                    value=2000,
                    minimum=1000,
                    maximum=5000
                )
                
                meal_count = gr.Slider(
                    label="Number of Meals",
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1
                )
                
                generate_btn = gr.Button(
                    "🚀 Generate Meal Plan",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column():
                gr.Markdown("### 🎯 Your Meal Plan")
                
                output = gr.Markdown(
                    label="Generated Meal Plan",
                    value="Your meal plan will appear here..."
                )
        
        gr.Markdown(
            """
            ---
            
            ### 💡 Tips:
            - Take a clear, well-lit photo of your fridge contents
            - Include receipts for recently purchased items
            - Select all relevant dietary constraints
            - Adjust calorie target based on your goals
            
            ### 🔧 How it works:
            1. **Vision Tool** extracts ingredients from photos
            2. **Receipt OCR** processes grocery receipts
            3. **Normalizer** standardizes ingredient names
            4. **Recipe Search** finds matching recipes
            5. **Nutrition Calculator** optimizes meal selection
            6. **Gemini Pro** generates the final plan with reasoning
            """
        )
        
        # Event handler
        generate_btn.click(
            fn=create_meal_plan,
            inputs=[
                fridge_image,
                receipt_image,
                dietary_constraints,
                calorie_target,
                meal_count
            ],
            outputs=output
        )
    
    return app


def main():
    """Launch the Gradio app"""
    app = create_ui()
    
    print("\n" + "="*50)
    print("🍳 Starting ChefByte Gradio UI...")
    print("="*50 + "\n")
    
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
