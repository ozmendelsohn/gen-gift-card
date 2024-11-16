import logging
import httpx
from pathlib import Path
from .base import ImageGenerator

logger = logging.getLogger(__name__)

class PicsumGenerator(ImageGenerator):
    def __init__(self, api_key: str = None, images_dir: Path = None):
        self.base_url = "https://picsum.photos"
        
    async def generate(self, prompt: str, occasion: str = None) -> bytes:
        try:
            logger.info(f"Generating image with Lorem Picsum")
            
            # Use simple URL format
            image_url = f"{self.base_url}/512"
            logger.info(f"Picsum URL: {image_url}")
            
            # Download the image
            async with httpx.AsyncClient() as client:
                # Follow redirects automatically
                response = await client.get(image_url, follow_redirects=True)
                
                if response.status_code != 200:
                    raise Exception(f"Picsum API error: Status {response.status_code}")
                
                return response.content

        except Exception as e:
            logger.error(f"Picsum generation error: {str(e)}")
            logger.exception("Full traceback:")
            raise 