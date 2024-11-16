from abc import ABC, abstractmethod
from pathlib import Path

class ImageGenerator(ABC):
    """Abstract base class for image generators"""
    
    @abstractmethod
    async def generate(self, prompt: str, occasion: str = None) -> bytes:
        """Generate an image and return the image data"""
        pass