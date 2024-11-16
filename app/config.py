from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# App configuration
class Settings:
    BASE_DIR = BASE_DIR
    UPLOAD_FOLDER = BASE_DIR / 'static/images/uploads'
    DEFAULT_CARD_PATH = BASE_DIR / 'static/images/default_card.png'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_MODEL = "llama3.2:1b"
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM = os.getenv("EMAIL_FROM")

settings = Settings()

# Create necessary directories
settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Create default card if it doesn't exist
if not settings.DEFAULT_CARD_PATH.exists():
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a simple default card
    img = Image.new('RGB', (1024, 1024), color='white')
    d = ImageDraw.Draw(img)
    
    # Add some text
    d.text((512, 512), "Gift Card", fill='black', anchor="mm")
    d.text((512, 562), "Image generation failed", fill='gray', anchor="mm")
    
    # Save the image
    settings.DEFAULT_CARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(settings.DEFAULT_CARD_PATH) 