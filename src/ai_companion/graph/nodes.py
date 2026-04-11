import os
from uuid import uuid4

from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from ai_companion.graph.states import AICompanionState
from ai_companion.graph.utils.chains import (
    get_chat_model,
    get_router_chain,
    get_character_card_chain
)
from ai_companion.graph.utils.helpers import get_text_to_speech_model
from ai_companion.modules.memory.long_term.memory_manager import get_memory_manager
from ai_companion.settings import settings



async def router_node(state: AICompanionState) -> AICompanionState:
    """Baed on the input this node will analyse and route to the next node. It may be video, audio or text node
       Returns:
        anyone of the type: 'conversation', 'image', 'audio'
    """
    router_chain = get_router_chain()
    response = await router_chain.ainvoke({"messages": state["messages"][-settings.ROUTER_MESSAGES_TO_ANALYZE :]})
    return {"workflow": response.response_type}

async def  memory_extraction_node(state: AICompanionState):
    """Extract and store important information from the last messages"""
    if not state["messages"]:
        return {}
    memory_manager = get_memory_manager()
    await memory_manager.extract_and_store_memories(state["messages"][-1])
    return {}

def context_injection_node(state: AICompanionState):
    """Inject ava's current activity into the current context inorder to improve the realism and simulated life"""
    
    pass

async def memory_injection_node(state: AICompanionState):
    """Fetches top k memories similar to current conversation and inject it into current context so the response will be based on previous conversation also"""
    memory_manager = get_memory_manager()
    recent_context = " ".join([m.content for m in state["messages"][-3:]])
    memories = await memory_manager.get_relevant_memories(recent_context)
    print(memories,"memories")
    memory_context = memory_manager.format_memories_for_prompt(memories=memories)
    return {"memory_context" : memory_context}

async def audio_node(state: AICompanionState, config: RunnableConfig):
    """Handles all audio related input and generate response"""
    memory_context = state["memory_context"]
    chain = get_character_card_chain(state.get("summary", ""))
    text_to_speech_module = get_text_to_speech_model()
    response = await chain.ainvoke(
        {
            "messages" : state["messages"],
            "memory_context": memory_context
        },
        config,
    )
    output_audio = await text_to_speech_module.synthesize(response)

    return {"messages": response, "audio_buffer": output_audio}


async def conversation_node(state: AICompanionState, config: RunnableConfig):
    """Handles all general text conversation and generate reponse based on that"""
    memory_context = state.get("memory_context")
    chain = get_character_card_chain(state.get("summary" , ""))
    response = await chain.ainvoke(
        {
            "messages": state["messages"],
            "memory_context": memory_context
        },
        config
    )
    return {"messages": AIMessage(content=response)}


async def image_node(state: AICompanionState, config:RunnableConfig):
    """Handles all image related input and generate response based on that"""
    pass

async def summarize_conversation_node(state: AICompanionState):
    """Summarize a list of conversation once a threashold is reached. This helps us to compress a lot of data into a summarized context to reduce token limit"""
    pass

