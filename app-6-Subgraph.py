# Problem statement: Before sending a query to specialist agent, we want to run a reusable precheck workflow:
# Validate query
# Detect urgency
# Return to parent graph

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class SupportState(TypedDict, total = False):
    query: str
    is_valid: bool
    urgency: Literal["low", "medium", "high"]
    answer: str

# Subgraph: precheck workflow
def validate_query(state: SupportState) -> SupportState:
    query = state.get("query", "").strip()

    if len(query) < 5:
        return {"is_valid": False}
    return {"is_valid": True}

def detech_urgency(state: SupportState) -> SupportState:
    query = state["query"].lower()

    if "urgent" in query or "immediately" in query or "critical" in query:
        urgency = "high"
    elif "soon" in query:
        urgency = "medium"
    else:
        urgency = "low"

    return {"urgency": urgency}

precheck_builder = StateGraph(SupportState)

precheck_builder.add_node("validate_query", validate_query)
precheck_builder.add_node("detech_urgency", detech_urgency)

precheck_builder.add_edge(START, "validate_query")
precheck_builder.add_edge("validate_query", "detech_urgency")
precheck_builder.add_edge("detech_urgency", END)

precheck_graph = precheck_builder.compile()

# PARENT GRAPH
def support_agent(state: SupportState) -> SupportState:
    if not state["is_valid"]:
        return {"answer": "please provide a more detailed query."}
    if state["urgency"] == "high":
        return {"answer": "Your issue has been marked as high priority. Our team will respond quickly."}
    return {"answer": "Your query has been received. Our support team will assist you shortly."}

parent_builder = StateGraph(SupportState)

parent_builder.add_node("precheck", precheck_graph)
# subgraph-precheck_graph being added as a node to the parent graph
parent_builder.add_node("support_agent", support_agent)

parent_builder.add_edge(START, "precheck")
parent_builder.add_edge("precheck", "support_agent")
parent_builder.add_edge("support_agent", END)

parent_graph = parent_builder.compile()

# while invoking the parent graph, subgraph will automatically be invoked
result = parent_graph.invoke({
    "query": "This is urgent, my payment is stuck."
})

print(result)