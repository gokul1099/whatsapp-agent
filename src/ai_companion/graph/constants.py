from enum import Enum
from typing import Optional

class WorkflowType(str, Enum):
    CONVERSATION = "conversation"
    IMAGE = "image"
    AUDIO = "audio"

class NodeName(str, Enum):
    MEMORY_EXTRACTION = "memory_extraction_node"
    ROUTER = "router_node"
    CONTEXT_INJECTION = "context_injection"
    MEMORY_INJECTION = "memory_injection"
    AUDIO = "audio_node"
    IMAGE = "image_node"
    CONVERSATION = "conversation_node"
    SUMMARIZE_CONVERSATION = "sumarrize_conversation_node"
