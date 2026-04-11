import os
import tempfile
from typing import Optional

from groq import Groq
from ai_companion.settings import settings

class SpeechToText:
    """A class to handle speech-to-text conversion using groq's whisper model.
    """

    def __init__(self):
        """Initialize SpeechToText class"""
        self._client: Optional[Groq] = None

    @property
    def client(self) -> Groq:
        """Get or create a Groq client instance using singleton pattern"""
        if self._client is None:
            self._client = Groq()
        return self._client
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Convert speech to text using Groq's whisper model
        
        Args:
            audio_data: Binary audio data
        Returns:
            str: The transcribed text
        
        Raises:
            ValueError: If the audio file is empty or invalid
            RuntimeError: If the transcription fails
        """

        if not audio_data:
            raise ValueError("Audio data cannot be empty")
        
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                with open(temp_file_path, "rb") as temp_audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=temp_audio_file,
                        model=settings.STT_MODEL_NAME,
                        language="en",
                        response_format="text"
                    )
                if not transcription:
                    raise ValueError("Transcription result is empty")
                return transcription
            finally:
                os.unlink(temp_file_path)
        except Exception as e:
            raise ValueError(f"Speech to text error : {e}")
                