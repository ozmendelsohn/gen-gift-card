import logging
import httpx
from pathlib import Path
import os
from .base import ImageGenerator
import json
import asyncio

logger = logging.getLogger(__name__)

class OpenAIGenerator(ImageGenerator):
    def __init__(self, api_key: str, images_dir: Path):
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/images/generations"

    async def generate(self, prompt: str, occasion: str = None) -> bytes:
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            logger.info(f"Using API key: {self.api_key[:6]}...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "url",
                "model": "dall-e-3"  # Changed to DALL-E 2 which is faster
            }
            
            logger.info(f"Sending request to OpenAI with data: {json.dumps(data, indent=2)}")
            
            # Increased timeout and added limits
            limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
            timeout = httpx.Timeout(timeout=60.0, connect=30.0)
            
            async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
                # Add retry logic
                for attempt in range(3):  # Try up to 3 times
                    try:
                        response = await client.post(
                            self.api_url,
                            headers=headers,
                            json=data
                        )
                        break  # If successful, break the retry loop
                    except (httpx.TimeoutException, httpx.NetworkError) as e:
                        if attempt == 2:  # Last attempt
                            raise  # Re-raise the last error
                        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(1)  # Wait before retrying
                
                logger.info(f"OpenAI Response Status: {response.status_code}")
                logger.info(f"OpenAI Response Headers: {dict(response.headers)}")
                logger.info(f"OpenAI Response Body: {response.text}")
                
                if response.status_code != 200:
                    error_detail = response.json() if response.text else "No error details"
                    raise Exception(f"OpenAI API error: Status {response.status_code}, Details: {error_detail}")

                response_data = response.json()
                image_url = response_data["data"][0]["url"]
                logger.info(f"Got image URL: {image_url}")
                
                # Download the image with retry logic
                for attempt in range(3):
                    try:
                        image_response = await client.get(image_url)
                        if image_response.status_code == 200:
                            return image_response.content
                        else:
                            raise Exception(f"Failed to download image: Status {image_response.status_code}")
                    except (httpx.TimeoutException, httpx.NetworkError) as e:
                        if attempt == 2:
                            raise
                        logger.warning(f"Download attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            logger.exception("Full traceback:")
            raise