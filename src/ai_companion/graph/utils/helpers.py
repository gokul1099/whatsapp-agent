import re

from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

from ai_companion.settings import settings


def get_chat_model(temperature: float= 0.7):
    """Create a instance of the chatmodel and return it"""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.TEXT_MODEL_NAME,
        temperature=temperature
    )

def get_text_to_speech_model():
    """Return text to speech model"""
    pass

def get_image_to_text_model():
    """Return image to text model"""
    pass

def remove_asterisk_content(text: str) -> str:
    """Remove content between asterisks form the text"""
    return re.sub(r"\*.*?\*", "", text).strip()


class AsteriskRemovalParser(StrOutputParser):
    def parse(self,text):
        return remove_asterisk_content(super().parse(text))
