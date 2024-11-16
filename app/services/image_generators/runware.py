import logging
import httpx
from pathlib import Path
import json
from .base import ImageGenerator
import base64

logger = logging.getLogger(__name__)

class RunwareGenerator(ImageGenerator):
    def __init__(self, api_key: str, images_dir: Path = None):
        self.api_key = api_key
        self.api_url = "https://api.runware.ai/v1"
        self.model_id = "runware:100@1"  # Default model ID

    async def generate(self, prompt: str, occasion: str = None) -> bytes:
        try:
            logger.info(f"Generating image with Runware API. Prompt: {prompt}")
            
            # Prepare the request payload
            payload = [
                {
                    "taskType": "authentication",
                    "apiKey": self.api_key
                },
                {
                    "taskType": "imageInference",
                    "taskUUID": "39d7207a-87ef-4c93-8082-1431f9c1dc97",
                    "positivePrompt": prompt,
                    "width": 512,
                    "height": 512,
                    "modelId": self.model_id,
                    "numberResults": 1
                }
            ]
            
            headers = {
                "Content-Type": "application/json"
            }
            
            logger.info("Sending request to Runware API")
            
            # Set up timeout and limits
            timeout = httpx.Timeout(timeout=60.0)
            limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
            
            async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                logger.info(f"Runware Response Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_detail = response.text
                    raise Exception(f"Runware API error: Status {response.status_code}, Details: {error_detail}")

                # Parse the response
                response_data = response.json()
                logger.info(f"Runware response: {json.dumps(response_data, indent=2)}")

                # Extract the image URL from the response
                if "data" in response_data and len(response_data["data"]) > 0:
                    image_url = response_data["data"][0].get("imageURL")
                    if not image_url:
                        raise Exception("No image URL in response")
                        
                    logger.info(f"Got image URL: {image_url}")
                    
                    # Download the image
                    image_response = await client.get(image_url)
                    if image_response.status_code != 200:
                        raise Exception(f"Failed to download image: Status {image_response.status_code}")
                    
                    return image_response.content
                else:
                    raise Exception("No data in response")

        except Exception as e:
            logger.error(f"Runware generation error: {str(e)}")
            logger.exception("Full traceback:")
            raise 