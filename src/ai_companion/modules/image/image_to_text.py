import base64
import logging
import os
from typing import Optional, Union

from ai_companion.settings import settings
from groq import Groq


class ImageToText:
    """A class to handle image-to-text conversion using Groq's vision capabilities"""
    def __init__(self):
        self._client: Optional[Groq]= None
        self.logger = logging.getLogger(__name__)

    @property
    def client(self) -> Groq:
        """Get ro create a single instance using singleton pattern"""
        if self._client is None:
            self._client = Groq()
        return self._client
    
    async def analyze_image(self, image_data: Union[str, bytes], prompt: str = "") -> str:
        """Analyze an image using Groq's vision capabilities
        
        Args:   
            image_data: Eithere a file path (str) or binary image data (bytes)
            prompt: Optional prompt to guide the image analysis
        
        Returns:
            str: image analysis or description
        
        Raises:
            ValueError: if the image data is empty or invalid
        """

        try:
            if isinstance(image_data, str):
                if not os.path.exists(image_data):
                    raise ValueError(f"Image path not found : {image_data}")
                with open(image_data, "rb") as image_file:
                    image_bytes = image_file.read()
            else:
                image_bytes = image_data
            if not image_bytes:
                raise ValueError("Image data cannot be empty")
            
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            if not prompt:
                prompt = "Please describe what you see in the image in details"

            messages = [
                {
                    "role": "user",
                    "content":[
                        {"type": "image_url",
                         "image_url":{"url": f"data:image/jpeg;base64,{base64_image}"}
                         }
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=settings.ITT_MODEL_NAME,
                messages=messages,
                max_tokens=1000,
            )

            if not response.choices:
                raise ValueError("No response received from groq api")
        
            description = response.choices[0].message.content
            self.logger.info(f"Generated image description: {description}")

            return description
        
        except Exception as e:
            raise ValueError(f"Failed to analyse image: {str(e)}") from e