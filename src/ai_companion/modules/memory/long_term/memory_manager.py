import logging
import uuid
from datetime import datetime
from typing import List, Optional

from ai_companion.core.prompt import MEMORY_EXTRACTION_PROMPT
from ai_companion.modules.memory.long_term.vector_store import get_vector_store
from ai_companion.settings import settings
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


class MemoryAnalysis(BaseModel):
    """Result of analyzing a message for memory-worthy content"""
    is_important: bool= Field(
        ...,
        description="Wehther the message is important enough to be stored as memory"
    )
    formatted_memory: Optional[str] = Field(
        ...,
        description="The formatted memory to be stored"
    )


class MemoryManager:
    """Manager class for handling long-term memory operations"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.logger = logging.getLogger(__name__)
        self.llm = ChatGroq(
            model = settings.SMALL_TEXT_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1,
            max_retries=2
        ).with_structured_output(MemoryAnalysis)
    
    async def _analyse_memory(self, message: str):
        """Analyses a memory to determine importane anf format if needed"""
        prompt = MEMORY_EXTRACTION_PROMPT.format(message=message)
        return await self.llm.ainvoke(prompt)

    async def extract_and_store_memories(self, message: BaseMessage) -> None:
        """Extract important information from message and store it in logn term memory"""
        if message.type != "human":
            return
        
        message_analysis: MemoryAnalysis = await self._analyse_memory(message=message.content)
        if message_analysis.is_important:
            ##Check similart memory already exists
            similar_memories = self.vector_store.find_simialar_memory(message_analysis.formatted_memory)
            if similar_memories:
                #skip storage if we already have similar memory
                self.logger.info(f"similar memory found, {message_analysis.formatted_memory}, Skipping")
                return
            
            self.logger.info(f"Storing the new memory, {message_analysis.formatted_memory}")
            self.vector_store.store_memory(
                text = message_analysis.formatted_memory,
                metadata={
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat()
                }
                )
    async def get_relevant_memories(self, context: str) -> List[str]:
        """Extract relevant memories to last conversation and return in for memory injection"""
        if not context:
            return []
        memories = self.vector_store.search_memories(query=context, k=settings.MEMORY_TOP_K)
        if memories:
            for memory in memories:
                self.logger.debug(f"Memory: `{memory.text}`")
        return [memory.text for memory in memories]

    def format_memories_for_prompt(self, memories: List[str]) -> str:
        if not memories:
            return ""
        return "\n".join(f"- {memory}" for memory in memories)
        

def get_memory_manager() -> MemoryManager:
    return MemoryManager()
