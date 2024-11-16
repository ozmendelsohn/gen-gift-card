import logging
import torch
from pathlib import Path
from diffusers import StableDiffusionPipeline
from .base import ImageGenerator
from io import BytesIO

logger = logging.getLogger(__name__)

class HuggingFaceGenerator(ImageGenerator):
    def __init__(self, model_id: str, images_dir: Path):
        self.model_id = model_id
        
        # Initialize the pipeline
        logger.info(f"Loading model: {model_id}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            safety_checker=None
        )
        self.pipe = self.pipe.to(self.device)
        
        if self.device == "cuda":
            self.pipe.enable_attention_slicing()
            
        logger.info(f"Model loaded on {self.device}")

    async def generate(self, prompt: str, occasion: str = None) -> bytes:
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Generate the image
            image = self.pipe(
                prompt=prompt,
                negative_prompt="blurry, low quality, distorted, deformed",
                num_inference_steps=30,
                guidance_scale=7.5,
                height=512,
                width=512
            ).images[0]
            
            # Convert PIL Image to bytes
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return buffered.getvalue()

        except Exception as e:
            logger.error(f"HuggingFace generation error: {str(e)}")
            raise