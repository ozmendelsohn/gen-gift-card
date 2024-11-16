from app.services.llm_service import LLMService
from app.services.image_service import ImageService

class ServiceFactory:
    _llm_service: LLMService = None
    _image_service: ImageService = None

    @classmethod
    def get_llm_service(cls) -> LLMService:
        if cls._llm_service is None:
            cls._llm_service = LLMService()
        return cls._llm_service

    @classmethod
    def get_image_service(cls) -> ImageService:
        if cls._image_service is None:
            cls._image_service = ImageService()
        return cls._image_service 

if __name__ == "__main__":
    import asyncio
    
    async def test_services():
        # Test LLM Service
        print("\nTesting LLM Service initialization:")
        llm_service = ServiceFactory.get_llm_service()
        print(f"LLM Service instance: {llm_service}")
        
        # Test Image Service
        print("\nTesting Image Service initialization:")
        image_service = ServiceFactory.get_image_service()
        print(f"Image Service instance: {image_service}")
        
        # Test singleton behavior
        print("\nTesting singleton behavior:")
        llm_service2 = ServiceFactory.get_llm_service()
        image_service2 = ServiceFactory.get_image_service()
        
        print(f"LLM Services are same instance: {llm_service is llm_service2}")
        print(f"Image Services are same instance: {image_service is image_service2}")
        
        # Test basic functionality
        print("\nTesting basic service functionality:")
        analysis = await llm_service.analyze_input(
            "John",
            "Thank you for being a great mentor"
        )
        print(f"Analysis result: {analysis}")

    asyncio.run(test_services()) 