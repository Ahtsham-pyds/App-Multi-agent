


import operator
import os
from typing import TypedDict, Annotated
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.graph import StateGraph, END

# Note: You need to install langgraph and either pydot or pygraphviz.
# pip install langgraph pydot
# For the visualization to work, the Graphviz system tool must also be installed
# on your machine (e.g., `sudo apt-get install graphviz` on Linux).
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    print("Error: langgraph library not found. Please run: pip install langgraph")
    exit()
    
# 1. Define the Graph State
# This is the object passed between nodes.
class AgentState(TypedDict):
    """
    Represents the state of our agent's execution.
    - query: The user's initial question.
    - iterations: Counter for the number of steps taken.
    """
    query: str
    iterations: Annotated[int, operator.add]


# 2. Define the Nodes (Functions that update the state)
def planner_node(state: AgentState) -> AgentState:
    """Simulates a planning step, deciding the next action."""
    print("--- NODE: Planner executed. Determining next step. ---")
    query = state["query"]
    
    # Simple logic to simulate a decision
    if "data" in query.lower():
        next_step = "search_data"
    else:
        next_step = "respond"
    
    # We update the state to include the decision for the router
    return {"query": query, "iterations": 1, "decision": next_step}

def search_node(state: AgentState) -> AgentState:
    """Simulates a search or tool-use step."""
    print("--- NODE: Search executed. Gathering information. ---")
    # In a real agent, this would call a tool like Google Search
    return {"query": state["query"], "iterations": 1, "search_result": "Information found: The sky is blue."}

def responder_node(state: AgentState) -> AgentState:
    """Simulates the final LLM response generation step."""
    print("--- NODE: Responder executed. Generating final answer. ---")
    # In a real agent, this would compile the final response
    return {"query": state["query"], "iterations": 1, "final_answer": "Final response generated."}


# 3. Define the Conditional Edge (Router)
def router(state: AgentState) -> str:
    """A router node that determines the next step based on the planner's output."""
    print(f"--- ROUTER: Routing based on decision: {state.get('decision')} ---")
    if state.get("decision") == "search_data":
        return "search_needed"
    elif state.get("decision") == "respond":
        return "final_response"
    # Fallback/default if something goes wrong
    return "final_response" 


# 4. Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("planner", planner_node)
workflow.add_node("search_data", search_node)
workflow.add_node("respond", responder_node)

# Set the Entry Point
workflow.set_entry_point("planner")

# Add Edges
# After 'search_data', always go to 'respond'
workflow.add_edge("search_data", "respond")

# Conditional Edge (Router) from 'planner'
workflow.add_conditional_edges(
    "planner",  # Source node
    router,     # Router function
    {           # Mapping of router output keys to destination nodes/END
        "search_needed": "search_data",
        "final_response": "respond",
    },
)

# Set the End Point
# The 'respond' node signals the end of the process
workflow.add_edge("respond", END)

# Compile the Graph
app = workflow.compile()

# This code snippet is generating a PNG image of the workflow graph using the Mermaid library. Here's
# a breakdown of what each part of the code is doing:
# png_bytes = app.get_graph().draw_mermaid_png(
#     draw_method=MermaidDrawMethod.PYPPETEER
# )

output_filename = "langgraph_flow.png"
app.get_graph().draw_png(output_filename)
