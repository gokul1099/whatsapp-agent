import os
import tempfile
from typing import Optional
import base64
from openai import OpenAI
from ai_companion.settings import settings

class TextToSpeech:
    """A class to handle text-to-speech"""

    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI()
        return self._client
    
    
    async def synthesize(self,text: str) -> bytes:
        """Convert text to speech
        
        Args:
            text: text string that has to be converted to speech
        
        return:
            bytes: generated speech 
        
        Raises:
            ValueError: If the input text is empty or too long
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty")

        if len(text) > 5000:
            raise ValueError("Input text exceeds maximum length of 5000 characters")
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini-audio-preview",
                modalities=["text","audio"],
                audio={"voice": "alloy", "format":"wav"},
                messages=[
                    {
                        "role":"user",
                        "content": text
                    }
                ]
            )
            audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
            with open("data.wav", "wb") as file:
                file.write(audio_bytes)
            return audio_bytes
        
        except Exception as e:
            raise ValueError(f"Text to speech conversion failed:{str(e)}") from e