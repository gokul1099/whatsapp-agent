from ai_companion.graph.states import AICompanionState
from langgraph.graph import END
from ai_companion.settings import settings
from typing import Literal


def should_summarize_conversation(state: AICompanionState) -> Literal["summarize_conversation_node", "__end__"]:
    messages = state["messages"]
    if len(messages) > settings.TOTAL_MESSAGE_AFTER_SUMMARY:
        return "summarize_conversation_node"
    return END

def select_workflow(state: AICompanionState) -> Literal["conversation_node", "image_node", "audio_node"]:
    workflow = state["workflow"]
    if workflow == "image":
        return "image_node"
    elif workflow == "audio":
        return "audio_node"
    else:
        return "conversation_node"