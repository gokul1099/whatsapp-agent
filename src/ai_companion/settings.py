from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(env_file=".env")
	
	OPENAI_API_KEY:str
	GROQ_API_KEY: str
	ELEVENLABS_API_KEY: str
	ELEVANLABA_VOICE_ID: str
	TOGETHER_API_KEY: str



	QDRANT_API_KEY: str | None
	QDRANT_URL: str
	QDRANT_PORT : str = "6333"
	QDRANY_HOST: str | None = None

	MEMORY_EMBEDDING_MODEL: str = "text-embedding-3-small"
	EMBEDDING_DIMENSION = 1536  # text-embedding-3-small dimension
	TEXT_MODEL_NAME: str = "llama-3.3-70b-versatile"
	SMALL_TEXT_MODEL: str = "gemma2-9b-it"
	STT_MODEL_NAME:str  = "whisper-large-v3-turbo"
	TTS_MODEL_NAME: str = "eleven_flash_v2_5"
	TTI_MODEL_NAME: str = "black-forest-labs/FLUX.1-schnell-Free"
	ITT_MODEL_NAME: str = "llama-3.2-90b-vision-previow"


	MEMORY_TOP_K: int = 3
	ROUTER_MESSAGES_TO_ANALYZE: int = 3
	TOTAL_MESSAGE_SUMMARY_TRIGGER: int =20
	TOTAL_MESSAGE_AFTER_SUMMARY: int = 5

	SHORT_TERM_MEMORY_DB_PATH: str = "/app/data/memory.db"



settings = Settings()