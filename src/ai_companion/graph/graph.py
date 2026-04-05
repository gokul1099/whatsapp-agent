from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from ai_companion.graph.edges import (select_workflow, should_summarize_conversation)
from ai_companion.graph.constants import NodeName
from ai_companion.graph.nodes import (
    router_node,
    memory_extraction_node,
    context_injection_node,
    memory_injection_node,
    audio_node,
    conversation_node,
    image_node,
    summarize_conversation_node
)
from ai_companion.graph.states import AICompanionState

@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(AICompanionState)

    ##Adding all the nodes
    graph_builder.add_node(NodeName.MEMORY_EXTRACTION,memory_extraction_node)
    graph_builder.add_node(NodeName.ROUTER, router_node)
    graph_builder.add_node(NodeName.CONTEXT_INJECTION, context_injection_node)
    graph_builder.add_node(NodeName.MEMORY_INDJECTION, memory_injection_node)
    graph_builder.add_node(NodeName.AUDIO, audio_node)
    graph_builder.add_node(NodeName.CONVERSATION, conversation_node)
    graph_builder.add_node(NodeName.IMAGE, image_node)
    graph_builder.add_node(NodeName.SUMMARIZE_CONVERSATION, summarize_conversation_node)

    #Define the flow
    #First extract memory from user message
    graph_builder.add_edge(START, NodeName.MEMORY_EXTRACTION)

    #add routing node define the type of response
    graph_builder.add_edge(NodeName.MEMORY_EXTRACTION, NodeName.ROUTER)

    #then inject context and memories
    graph_builder.add_edge(NodeName.ROUTER, NodeName.CONTEXT_INJECTION)
    graph_builder.add_edge(NodeName.CONTEXT_INJECTION, NodeName.MEMORY_INJECTION)

    ## based on the routed node response selecte next work flow. it may be "conversation","image",audio
    graph_builder.add_conditional_edges(NodeName.MEMORY_INJECTION, select_workflow)

    #Check whether to summarize the conversation or not
    graph_builder.add_conditional_edges(NodeName.CONVERSATION, should_summarize_conversation)
    graph_builder.add_conditional_edges(NodeName.IMAGE, should_summarize_conversation)
    graph_builder.add_conditional_edges(NodeName.AUDIO, should_summarize_conversation)

    graph_builder.add_edge(NodeName.SUMMARIZE_CONVERSATION, END)
    return graph_builder