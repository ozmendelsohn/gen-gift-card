import ollama
import json
import logging
from app.config import settings
from typing import Dict, Optional, Any
import httpx

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.model = settings.LLM_MODEL
        self.api_url = "http://127.0.0.1:11434/api/chat"  # Ollama API endpoint

    async def analyze_input(self, recipient_name: str, initial_thoughts: str) -> dict:
        """Analyze initial input and suggest options"""
        prompt = self._create_analysis_prompt(recipient_name, initial_thoughts)
        
        try:
            response = self._get_llm_response(prompt)
            return self._extract_json(response['message']['content'])
        except Exception as e:
            logger.error(f"LLM Analysis Error: {str(e)}")
            return self._get_fallback_analysis(initial_thoughts)

    async def generate_message(
        self,
        recipient_name: str,
        relationship: str,
        occasion: str,
        emotion: str,
        memories: str
    ) -> Dict[str, str]:
        """Generate personalized message and image prompt"""
        prompt = self._create_message_prompt(
            recipient_name, relationship, occasion, emotion, memories
        )
        
        try:
            response = self._get_llm_response(prompt)
            result = self._extract_json(response['message']['content'])
            return self._validate_message_response(result, recipient_name, occasion, emotion)
        except Exception as e:
            logger.error(f"Message Generation Error: {str(e)}")
            return self._get_fallback_message(recipient_name, occasion, emotion, memories)

    def _get_llm_response(self, prompt: str) -> dict:
        """Get response from LLM"""
        return ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}]
        )

    def _create_analysis_prompt(self, recipient_name: str, initial_thoughts: str) -> str:
        """Create prompt for input analysis"""
        return f"""
        Analyze this gift card message information and suggest appropriate options:
        
        Recipient Name: {recipient_name}
        Initial Message: {initial_thoughts}
        
        Based on the above, determine:
        1. The likely relationship between sender and recipient
        2. The probable occasion
        3. The main emotion being conveyed
        4. Any specific memories or references mentioned
        
        Respond in JSON format:
        {{
            "relationship": "colleague",
            "occasion": "retirement",
            "emotion": "gratitude",
            "memories": "working together",
            "explanation": "This appears to be a retirement gift for a colleague..."
        }}
        
        Only use:
        - relationship: ["family", "friend", "colleague", "other"]
        - occasion: ["birthday", "holiday", "thank_you", "congratulations", "other"]
        - emotion: ["joy", "gratitude", "love", "excitement"]
        """

    def _create_message_prompt(
        self,
        recipient_name: str,
        relationship: str,
        occasion: str,
        emotion: str,
        memories: str
    ) -> str:
        """Create prompt for message generation"""
        return f"""
        Create a heartfelt gift card message and image description based on:
        
        Recipient: {recipient_name}
        Relationship: {relationship}
        Occasion: {occasion}
        Emotion: {emotion}
        Memories: {memories}
        
        Return ONLY a JSON object:
        {{
            "message": "A warm, personal message without placeholders",
            "image_prompt": "A detailed visual description (20+ words)"
        }}
        """

    @staticmethod
    def _extract_json(content: str) -> dict:
        """Extract JSON from LLM response"""
        content = content.strip()
        start = content.find('{')
        end = content.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        raise ValueError("No valid JSON found in response")

    @staticmethod
    def _validate_message_response(
        result: dict,
        recipient_name: str,
        occasion: str,
        emotion: str
    ) -> dict:
        """Validate and possibly enhance the message response"""
        if not result.get("message") or not result.get("image_prompt"):
            return LLMService._get_fallback_message(recipient_name, occasion, emotion, "")
        
        # Ensure image prompt is detailed enough
        if len(result["image_prompt"].split()) < 20:
            result["image_prompt"] = (
                f"A professional greeting card design for {occasion}, "
                f"conveying {emotion}, with warm colors and elegant composition. "
                f"The scene should include elements that represent celebration and connection."
            )
        
        return result

    @staticmethod
    def _get_fallback_message(recipient_name: str, occasion: str, emotion: str, memories: str) -> dict:
        return {
            "message": (
                f"Dear {recipient_name},\n\n"
                f"I wanted to take this moment to share my {emotion} with you on your {occasion}. "
                f"{memories}\n\n"
                f"Best wishes"
            ),
            "image_prompt": (
                f"A professional greeting card design for {occasion}, "
                f"conveying {emotion}, with warm colors and elegant composition."
            )
        }

    @staticmethod
    def _get_fallback_analysis(initial_thoughts: str) -> dict:
        return {
            "relationship": "",
            "occasion": "",
            "emotion": "",
            "memories": initial_thoughts,
            "explanation": "Could not automatically analyze the input. Please select options manually."
        } 

if __name__ == "__main__":
    import asyncio
    
    async def test_llm_service():
        service = LLMService()
        
        print("\nTesting analyze_input:")
        result = await service.analyze_input(
            "John Smith",
            "Thanks for being a great mentor during my internship. Your guidance was invaluable."
        )
        print(f"Analysis result: {json.dumps(result, indent=2)}")
        
        print("\nTesting generate_message:")
        message_result = await service.generate_message(
            recipient_name="John Smith",
            relationship="colleague",
            occasion="thank_you",
            emotion="gratitude",
            memories="mentoring during internship"
        )
        print(f"Message generation result: {json.dumps(message_result, indent=2)}")

    asyncio.run(test_llm_service()) 