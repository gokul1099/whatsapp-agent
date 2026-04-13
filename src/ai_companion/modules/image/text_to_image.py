import base64
import logging
import os
from typing import Optional

from ai_companion.core.prompt import IMAGE_ENHANCEMENT_PROMPT, IMAGE_SCENARIO_PROMPT
from ai_companion.settings import settings
from langchain_classic.prompts import PromptTemplate
from langchain_groq import ChatGroq
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from PIL import Image
import io

class ScenarioPrompt(BaseModel):
    """Class for scenario response"""

    narrative: str = Field(..., description="The AI's narrative response to the question")
    image_prompt:str = Field(..., description="The visual prompt to generate an image representing the scene")

class EnhancedPrompt(BaseModel):
    """Class for text prompt"""
    content: str = Field(..., description="The enhanced text prompt to generate an image")


class TextToImage:
    """A class to handle text-to-image generation """
    def __init__(self):
        self._genai_client: Optional[genai.Client] = None
        self.logger = logging.getLogger(__name__)
    
    @property
    def genai_client(self):
        if self._genai_client is None:
            self._genai_client = genai.Client()
        return self._genai_client

    async def generate_image(self, prompt:str , output_path: str ="") -> bytes:
        """Generate an image from a prompt """
        if not prompt.strip():
            raise ValueError("prompt not found")

        try:
            self.logger.info(f"Generating image for prompt: {prompt}")

            # response = await self.openai_client.responses.create(
            #     model="dall-e-2",
            #     input=prompt,
            #     tools=[
            #         {
            #             "type":"image_generation",
            #             "background":"transparent",
            #             "quality":"medium"
            #         }
            #     ]
            # )
            response = self.genai_client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=[prompt]
            )
            for part in response.parts:
                if part.inline_data is not None:
                    image = Image.open(io.BytesIO(part.inline_data.data))
                    if output_path:
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        image.save(output_path)
                        self.logger.info(f"Generated image saved locally at: {output_path}")

            with open(output_path, "rb") as image_file:
                binary_data = image_file.read()
                base64_bytes = base64.b64encode(binary_data)
                base64_string = base64_bytes.decode("utf-8")
            return base64_string
        except Exception as e:
            raise ValueError(f"Failed to generate image: {str(e)}") from e
    

    async def create_scenario(self, chat_history: list = None) -> ScenarioPrompt:
        """Creates a first-person narrative scenario and corresponding image prompt based on chat history."""
        try:
            formatted_history = "\n".join([f"{msg.type.title()}: {msg.content}" for msg in chat_history[-5:]])
            self.logger.info("Creating scenario from chat history")
            llm = ChatGroq(
                model=settings.TEXT_MODEL_NAME,
                api_key=settings.GROQ_API_KEY,
                temperature=0.4,
                max_retries=2
            )
            structured_llm = llm.with_structured_output(ScenarioPrompt)
            chain = (PromptTemplate(
                input_variables=["chat_history"],
                template=IMAGE_SCENARIO_PROMPT
            )
            | structured_llm
            )

            scenario = chain.invoke({"chat_history": formatted_history})
            self.logger.info(f"Created Scenario: {scenario}")

            return scenario
        except Exception as e:
            raise ValueError(f"Failed to create scenario: {str(e)}") from e
    
    async def enhance_prompt(self, prompt: str) -> str:
        """Enhance a simple prompt with additional details and context."""
        try:
            self.logger.info(f"Enhancing prompt: '{prompt}'")
            llm = ChatGroq(
                model=settings.TEXT_MODEL_NAME,
                api_key=settings.GROQ_API_KEY,
                temperature=0.25,
                max_retries=2
            )

            structured_llm = llm.with_structured_output(EnhancedPrompt)
            chain = (
                PromptTemplate(
                    input_variables=["prompt"],
                    template=IMAGE_ENHANCEMENT_PROMPT
                )
                | structured_llm
            )

            enhanced_prompt = chain.invoke({"prompt": prompt}).content
            self.logger.info(f"Enahnced prompt: '{enhanced_prompt}'")
            return enhanced_prompt
        except Exception as e:
            raise ValueError(f"Failed to enhance prompt: {str(e)}") from e
            
        
