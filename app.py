from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import io
import base64
import os
from pathlib import Path
import json
import ollama
from diffusers import StableDiffusionPipeline
import torch
from urllib.parse import quote
import time

# Get the current directory
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates configuration
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configuration
UPLOAD_FOLDER = BASE_DIR / 'static/images/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload folder if it doesn't exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize Stable Diffusion
pipe = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-3.5-medium",
    torch_dtype=torch.float16,
    use_safetensors=True
)
if torch.cuda.is_available():
    pipe = pipe.to("cuda")
else:
    pipe = pipe.to("cpu")

async def analyze_initial_input(recipient_name: str, initial_thoughts: str) -> dict:
    """Use LLM to analyze initial input and suggest questionnaire options"""
    
    prompt = f"""
    Analyze this gift card message information and suggest appropriate options:
    
    Recipient Name: {recipient_name}
    Initial Message: {initial_thoughts}
    
    Based on the above, determine:
    1. The likely relationship between sender and recipient
    2. The probable occasion
    3. The main emotion being conveyed
    4. Any specific memories or references mentioned
    
    Respond in JSON format like this example:
    {{
        "relationship": "colleague",
        "occasion": "retirement",
        "emotion": "gratitude",
        "memories": "working together",
        "explanation": "This appears to be a retirement gift for a colleague, expressing gratitude for their time working together."
    }}
    
    Only use the following values:
    - relationship: ["family", "friend", "colleague", "other"]
    - occasion: ["birthday", "holiday", "thank_you", "congratulations", "other"]
    - emotion: ["joy", "gratitude", "love", "excitement"]
    """
    
    try:
        response = await ollama.chat(
            model='llama2:13b',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        # Extract the JSON part from the response
        content = response['message']['content']
        # Find JSON content between curly braces
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            result = json.loads(json_str)
        else:
            raise ValueError("No valid JSON found in response")

        # Validate the response has required fields
        required_fields = ["relationship", "occasion", "emotion", "memories", "explanation"]
        if not all(field in result for field in required_fields):
            raise ValueError("Missing required fields in response")

        return result
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        print(f"Raw response: {response if 'response' in locals() else 'No response'}")
        
        # Return a more specific fallback based on the initial thoughts
        if "retirement" in initial_thoughts.lower():
            return {
                "relationship": "colleague",
                "occasion": "congratulations",
                "emotion": "gratitude",
                "memories": initial_thoughts,
                "explanation": "This appears to be a retirement message for a colleague."
            }
        
        return {
            "relationship": "",
            "occasion": "",
            "emotion": "",
            "memories": initial_thoughts,
            "explanation": "Could not automatically analyze the input. Please select options manually."
        }

async def generate_message_with_llm(
    recipient_name: str,
    relationship: str,
    occasion: str,
    emotion: str,
    memories: str
) -> dict:
    """Generate personalized message using LLM"""
    
    prompt = f"""
    Create a heartfelt gift card message based on the following information:
    
    Recipient: {recipient_name}
    Relationship: {relationship}
    Occasion: {occasion}
    Emotion to convey: {emotion}
    Specific memories/notes: {memories}
    
    Please provide your response in JSON format:
    {{
        "message": "The complete gift card message",
        "image_prompt": "A detailed prompt for generating an appropriate image for this message"
    }}
    
    The message should be personal and incorporate the specific memories if provided.
    The image prompt should describe a scene or image that matches the emotion and occasion.
    """
    
    try:
        response = await ollama.chat(
            model='llama2:13b',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        # Extract the JSON part from the response
        content = response['message']['content']
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = content[json_start:json_end]
            result = json.loads(json_str)
        else:
            raise ValueError("No valid JSON found in response")

        return result
    except Exception as e:
        print(f"Message Generation Error: {str(e)}")
        return {
            "message": f"Dear {recipient_name}, Thinking of you on this {occasion}. {memories}",
            "image_prompt": f"A warm and inviting {occasion} scene with {emotion} atmosphere"
        }

async def generate_image_with_stable_diffusion(prompt: str) -> str:
    """Generate image using Stable Diffusion"""
    try:
        # Add some context to the prompt for better results
        enhanced_prompt = f"high quality, detailed, professional greeting card style: {prompt}"
        
        # Generate the image
        image = pipe(enhanced_prompt).images[0]
        
        # Save the image
        image_path = UPLOAD_FOLDER / f"generated_{int(time.time())}.png"
        image.save(image_path)
        
        return str(image_path.relative_to(BASE_DIR))
    except Exception as e:
        print(f"Image Generation Error: {str(e)}")
        return "static/images/default_card.png"  # Fallback to default image

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-questionnaire")
async def start_questionnaire(
    request: Request,
    recipient_name: str = Form(...),
    initial_thoughts: Optional[str] = Form(None),
    gift_card_type: str = Form(...),
    amount: int = Form(...)
):
    # Analyze initial input with LLM
    suggestions = await analyze_initial_input(recipient_name, initial_thoughts or "")
    
    return templates.TemplateResponse("questionnaire.html", {
        "request": request,
        "recipient_name": recipient_name,
        "initial_thoughts": initial_thoughts,
        "suggestions": suggestions
    })

@app.post("/generate-message")
async def generate_message(
    request: Request,
    recipient_name: str = Form(...),
    relationship: str = Form(...),
    occasion: str = Form(...),
    emotion: str = Form(...),
    memories: Optional[str] = Form(None)
):
    try:
        # Generate message and image prompt
        generated_content = await generate_message_with_llm(
            recipient_name, relationship, occasion, emotion, memories
        )
        
        # Generate image using the prompt
        image_path = await generate_image_with_stable_diffusion(generated_content["image_prompt"])
        
        # Encode message for URL
        encoded_message = quote(generated_content["message"])
        
        return JSONResponse({
            "status": "success",
            "preview_url": f"/preview?message={encoded_message}&image={image_path}"
        })
    except Exception as e:
        print(f"Error in generate_message: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": "Failed to generate message and image"
        }, status_code=500)

@app.get("/preview")
async def preview(
    request: Request,
    message: str,
    image: str
):
    return templates.TemplateResponse("preview.html", {
        "request": request,
        "message": message,
        "image": image
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 