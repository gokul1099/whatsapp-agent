import logging
import uuid
from datetime import datetime
from typing import List, Optional

from ai_companion.modules.memory.long_term.vector_store import get_vector_store
from ai_companion.settings import settings
from langchain_core.messages import BaseMessage
from ai_companion.core.prompt import MEMORY_EXTRACTION_PROMPT
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field


class MemoryAnalysis(BaseModel):
    """Results of analysing a message for memory-worthy content."""
    is_important: bool = Field(..., description="Whether the message is important enough to be stored as a memory")
    formatted_memory: Optional[str] = Field(..., description="The formatted memory to be stored")

class MemoryManager:
    """Manager class for handling long-term memory operations."""
    def __init__(self):
        self.vector_store = get_vector_store()
        self.logger = logging.getLogger(__name__)
        self.llm = ChatGroq(
            model=settings.SMALL_TEXT_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.1,
            max_retries=2
        ).with_structured_output(MemoryAnalysis)
    
    async def _analyse_memory(self, message:str) -> MemoryAnalysis:
        """Analyse a message to determine importance and format if needed"""
        prompt = MEMORY_EXTRACTION_PROMPT.format(message)
        return await self.llm.ainvoke(prompt)
    
    async def extract_and_store_memories(self, message: BaseMessage):
        """Extract important information from a message and store in vector store"""
        if message.type != "human":
            return
        
        analysis: MemoryAnalysis = self._analyse_memory(message=message)
        if analysis.is_important and analysis.formatted_memory:
            similar =self.vector_store.search_memories(analysis.fomatter_memory)
            if similar:
                self.logger.info("Similar memory already exisits, `{analysis.formatted_memory}`")
                return

            self.logger.info("No similar memory found storing the new memoery: {analysis.formatter_memory}")
            self.vector_store.store_memory(
                text=analysis.formatted_memory,
                metadata={
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        
    def get_relevant_memories(self, context: str) -> List[str]:
        """Retrieve relevant memories based on the current context"""
        memories = self.vector_store.find_simialar_memory(context, k=settings.MEMORY_TOP_K)
        if memories:
            for memory in memories:
                self.logger.debug(f"Memory: '{memory.text}' (score: {memory.score:.2f})")
        return [memory.text for memory in memories]
    
    def format_memories_for_prompt(self, memories: List[str]) -> str:
        if not memories:
            return ""
        return "\n".join(f"- {memory}" for memory in memories)
def get_memory_manager()-> MemoryManager:
    return MemoryManager()