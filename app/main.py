from fastapi import FastAPI, Request, Form, Body, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse, Response
from typing import Optional
import logging
from urllib.parse import quote
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fpdf import FPDF
from PIL import Image
import os
from io import BytesIO
import qrcode
import base64
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.services.service_factory import ServiceFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory=str(settings.BASE_DIR / "static")), name="static")

# Templates configuration
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "templates"))

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-questionnaire")
async def start_questionnaire(
    request: Request,
    recipient_name: str = Form(...),
    initial_thoughts: Optional[str] = Form(None),
    gift_card_type: str = Form("general"),
    amount: int = Form(0)
):
    llm_service = ServiceFactory.get_llm_service()
    suggestions = await llm_service.analyze_input(recipient_name, initial_thoughts or "")
    
    return templates.TemplateResponse("questionnaire.html", {
        "request": request,
        "recipient_name": recipient_name,
        "initial_thoughts": initial_thoughts,
        "suggestions": suggestions
    })

@app.post("/generate-message")
async def generate_message(
    request: Request,
    relationship: str = Form(...),
    occasion: str = Form(...),
    emotion: str = Form(...),
    memories: Optional[str] = Form(None)
):
    try:
        # Get form data
        form_data = await request.form()
        recipient_name = form_data.get("recipient_name", "Friend")
        
        logger.info("=== Starting message generation ===")
        logger.info(f"Recipient: {recipient_name}")
        logger.info(f"Relationship: {relationship}")
        logger.info(f"Occasion: {occasion}")
        logger.info(f"Emotion: {emotion}")
        logger.info(f"Memories: {memories}")
        
        # Get services
        llm_service = ServiceFactory.get_llm_service()
        image_service = ServiceFactory.get_image_service()
        
        # Generate message and image prompt
        logger.info("Calling LLM service...")
        generated_content = await llm_service.generate_message(
            recipient_name, relationship, occasion, emotion, memories or ""
        )
        
        logger.info(f"LLM Response: {generated_content}")
        
        # Extract message
        message = generated_content["message"]
        logger.info(f"Message: {message}")
        
        # Generate image using the prompt
        logger.info("Calling image service...")
        image_path = await image_service.generate_image(
            generated_content["image_prompt"],
            occasion=occasion
        )
        logger.info(f"Image path: {image_path}")
        
        # Return the preview template with the generated content
        return templates.TemplateResponse("preview.html", {
            "request": request,
            "message": message,
            "image_path": image_path,
            "recipient_name": recipient_name
        })
        
    except Exception as e:
        logger.error(f"Error in generate_message: {str(e)}")
        logger.exception("Full traceback:")
        # Return to questionnaire with error and all necessary variables
        return templates.TemplateResponse("questionnaire.html", {
            "request": request,
            "error": f"Failed to generate message and image: {str(e)}",
            "recipient_name": recipient_name,
            "suggestions": {  # Add default suggestions
                "relationship": relationship,
                "occasion": occasion,
                "emotion": emotion,
                "memories": memories
            }
        }, status_code=500)

@app.post("/send-gift-card")
async def send_gift_card(request: Request):
    try:
        data = await request.json()
        recipient_email = data.get('email')
        message = data.get('message')
        gift_card_link = data.get('gift_card_link')
        
        # Create email
        msg = MIMEMultipart()
        msg['Subject'] = "You've received a gift card!"
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = recipient_email

        # Create HTML content
        html = f"""
        <html>
            <body>
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>You've received a gift card!</h2>
                    <div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        {message}
                    </div>
                    <div style="margin: 20px 0;">
                        <a href="{gift_card_link}" 
                           style="background: #007bff; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 6px;">
                            Redeem Your Gift Card
                        </a>
                    </div>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)

        return JSONResponse({
            "status": "success",
            "message": "Gift card sent successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to send gift card: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    try:
        data = await request.json()
        message = data.get('message')
        image_path = data.get('image_path')
        gift_card_link = data.get('gift_card_link')

        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Use Arial instead of DejaVu (Arial is built-in)
        pdf.set_font('Arial', 'B', 16)
        
        # Add title
        pdf.cell(0, 10, 'Your Gift Card', 0, 1, 'C')
        
        # Add message
        pdf.set_font('Arial', '', 12)
        # Split message into lines to handle long text
        lines = [line.strip() for line in message.split('\n') if line.strip()]
        for line in lines:
            pdf.multi_cell(0, 10, line)
        
        # Add some spacing
        pdf.ln(10)
        
        try:
            # Add gift card image
            if image_path.startswith('data:image'):
                # Handle base64 image
                image_data = image_path.split(',')[1]
                image = Image.open(BytesIO(base64.b64decode(image_data)))
                temp_path = "temp_image.png"
                image.save(temp_path)
                pdf.image(temp_path, x=10, w=190)
                os.remove(temp_path)
            else:
                # Handle regular image path
                full_path = os.path.join(os.getcwd(), image_path.lstrip('/'))
                if os.path.exists(full_path):
                    pdf.image(full_path, x=10, w=190)
                else:
                    logger.error(f"Image file not found: {full_path}")
        except Exception as img_error:
            logger.error(f"Error adding image to PDF: {str(img_error)}")
        
        # Add QR code
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(gift_card_link)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            qr_path = "temp_qr.png"
            qr_img.save(qr_path)
            
            # Add QR code to PDF
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Scan to Redeem Your Gift Card', 0, 1, 'C')
            pdf.image(qr_path, x=70, y=pdf.get_y()+10, w=70)
            os.remove(qr_path)
            
            # Add gift card link text
            pdf.set_y(pdf.get_y()+90)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, 'Or click this link to redeem:', 0, 1, 'C')
            pdf.set_text_color(0, 0, 255)
            pdf.cell(0, 10, gift_card_link, 0, 1, 'C', link=gift_card_link)
        except Exception as qr_error:
            logger.error(f"Error adding QR code to PDF: {str(qr_error)}")
        
        # Save PDF to a temporary file first
        temp_pdf_path = "temp_gift_card.pdf"
        pdf.output(temp_pdf_path)
        
        # Read the PDF file and return it
        with open(temp_pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        
        # Clean up the temporary PDF file
        os.remove(temp_pdf_path)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment;filename=gift-card.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ... (rest of your routes) 