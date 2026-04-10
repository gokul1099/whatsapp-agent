from ai_companion.graph.states import AICompanionState
from langgraph.graph import END
from ai_companion.settings import settings
from typing import Literal
from ai_companion.graph.constants import NodeName

def should_summarize_conversation(state: AICompanionState) -> Literal[NodeName.SUMMARIZE_CONVERSATION, "__end__"]:
    messages = state["messages"]
    if len(messages) > settings.TOTAL_MESSAGE_AFTER_SUMMARY:
        return NodeName.SUMMARIZE_CONVERSATION
    return END

def select_workflow(state: AICompanionState) -> Literal[NodeName.CONVERSATION, NodeName.IMAGE, NodeName.AUDIO]:
    workflow = state["workflow"]
    if workflow == "image":
        return NodeName.IMAGE
    elif workflow == "audio":
        return NodeName.AUDIO
    else:
        return NodeName.CONVERSATION