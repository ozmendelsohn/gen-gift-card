import logging
from pathlib import Path
import tempfile
from app.config import settings
from .image_generators.huggingface import HuggingFaceGenerator
from .image_generators.openai import OpenAIGenerator
from .image_generators.runware import RunwareGenerator
from .image_generators.picsum import PicsumGenerator
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        # Initialize the selected generator
        self.generator = self._initialize_generator()

    def _initialize_generator(self):
        """Initialize the appropriate generator based on configuration"""
        generator_type = os.getenv("IMAGE_GENERATOR", "picsum").lower()
        
        if generator_type == "picsum":
            logger.info("Initializing Picsum generator")
            return PicsumGenerator()
        elif generator_type == "runware":
            api_key = os.getenv("RUNWARE_API_KEY")
            if not api_key:
                logger.error("RUNWARE_API_KEY not found in environment variables")
                raise ValueError("RUNWARE_API_KEY environment variable is required for Runware generator")
            logger.info("Initializing Runware generator")
            return RunwareGenerator(api_key)
        elif generator_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment variables")
                raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI generator")
            logger.info("Initializing OpenAI generator")
            return OpenAIGenerator(api_key, None)
        else:
            logger.info("Initializing HuggingFace generator")
            return HuggingFaceGenerator("runwayml/stable-diffusion-v1-5", None)

    async def generate_image(self, prompt: str, occasion: str = None) -> str:
        """Generate an image using the configured generator"""
        try:
            # Generate and get the image data
            image_data = await self.generator.generate(prompt, occasion)
            
            # Convert image data to base64
            if isinstance(image_data, bytes):
                image_b64 = base64.b64encode(image_data).decode('utf-8')
            else:
                # If it's a PIL Image
                buffered = BytesIO()
                image_data.save(buffered, format="PNG")
                image_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Return data URL
            return f"data:image/png;base64,{image_b64}"
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return self._get_default_image(occasion)

    def _get_default_image(self, occasion: str) -> str:
        """Create and return a default image when generation fails"""
        # Create a new image with a solid background
        img = Image.new('RGB', (512, 512), color='#f0f0f0')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        text = f"Gift Card - {occasion.title() if occasion else 'Default'}"
        
        # Try to center the text (rough estimation)
        w, h = draw.textsize(text) if hasattr(draw, 'textsize') else (200, 20)
        draw.text(
            ((512 - w) / 2, (512 - h) / 2),
            text,
            fill='#333333'
        )
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"

if __name__ == "__main__":
    import asyncio
    
    async def test_image_service():
        service = ImageService()
        
        test_prompts = [
            ("A beautiful birthday celebration scene with cake and balloons", "birthday"),
            ("A thank you card with elegant flowers", "thank_you"),
            ("A winter holiday scene with snow and decorations", "holiday")
        ]
        
        for prompt, occasion in test_prompts:
            print(f"\nGenerating image for: {prompt}")
            image_path = await service.generate_image(prompt, occasion)
            print(f"Generated image data URL length: {len(image_path)}")

    asyncio.run(test_image_service())