from langgraph.graph import MessagesState
from ai_companion.graph.constants import WorkflowType
from typing import Optional
class AICompanionState(MessagesState):
    """State class for the AI companion workflow
    
    Extends MessagesState to track conversation history and maintains the last message received
    
    Attributes:
        last_message (AnyMessage): The most recent message inthe conversation, can be any valid 
            langchain message type (HumanMessage, AIMessage, etc.)
        workflow(str): the current workflow the AI companion is in. Can be "conversation", "image",
            "audio"
        audio_buffer(bytes): The audio buffer to be used for speech-to-text conversion
        current_activity: The current activity of Ava based on the schedule
        memory_context (str): The context of the memories to be injected into the character card.
    
    """

    summary: Optional[str]
    workflow: Optional[WorkflowType]
    audio_buffer: Optional[bytes]
    image_path: Optional[str]
    current_activity: Optional[str]
    apply_activity: Optional[bool]
    memory_context: Optional[str]



