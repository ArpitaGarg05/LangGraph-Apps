# Problem statement: Build a customer support system with:
# A classifier Node
# Billing Agent
# Technical Agent
# General Agent
# Quality Checker
# Final Response

from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class SupportState(TypedDict, total = False):
    query: str
    category: Literal["billing", "technical", "general"]
    # by defining category as literal, it can be billing , technical, or general only
    # it cannot be empty or anything else
    answer: str
    quality_score: int

def classify_query(state: SupportState) -> SupportState:
    """
    Supervisor-line node.
    It decides which speacialist agent should handle the query.
    """
    query = state["query"].lower()

    if "refund" in query or "payment" in query or "invoice" in query:
        category = "billing"
    elif "error" in query or "debug" in query or "not working" in query:
        category = "technical"
    else:
        category = "general"

    return {"category": category}

def route_to_agent(state: SupportState) -> str:
    """
    Routing function used by conditional edges.
    """
    return state["category"] # from the state return the category value

def billing_agent(state: SupportState) -> SupportState:
    return {
        "answer": (
            "Billing Agent: I checked your payment/refund related issue. "
            "Please share your order ID so we can verify transaction."
        )
    }

def technical_agent(state: SupportState) -> SupportState:
    return {
        "answer": (
            "Technical Agent: This looks like a technical issue. "
            "Please try clearing the cache and restarting the app. "
            "If the issue continues, share the error screenshot"
        )
    }

def general_agent(state: SupportState) -> SupportState:
    return {
        "answer": (
            "General Agent: Thanks for reaching out. "
            "I can help you with orders, refunds, product_details, or account_related queries."
        )
    }

def quality_checker(state: SupportState) -> SupportState:
    """
    Reviewer node.
    Checks if the answer is useful enough.
    """

    answer = state.get("answer", "")

    if len(answer) > 50:
        score = 5
    elif len(answer) > 40:
        score = 4
    elif len(answer) > 30:
        score = 3
    elif len(answer) > 20:
        score = 2
    elif len(answer) > 10:
        score = 1
    else:
        score = 0

    return {"quality_score": score}

def final_response(state: SupportState) -> SupportState:
    return {
        "answer": f"{state['answer']}\n\nQuality score: {state['quality_score']}/5"
    }

builder = StateGraph(SupportState)

builder.add_node("classify_query", classify_query)
builder.add_node("billing_agent", billing_agent)
builder.add_node("technical_agent", technical_agent)
builder.add_node("general_agent", general_agent)
builder.add_node("quality_checker", quality_checker)
builder.add_node("final_response", final_response)

builder.add_edge(START, "classify_query")

# next node that will be triggered depends upon the classify_query functionality
# if state['category'] == "billing":
#     call billing_agent
# elif state['category'] == "technical":
#     call technical_agent
builder.add_conditional_edges(
    "classify_query",
    route_to_agent,
    {
        "billing": "billing_agent",
        "technical": "technical_agent",
        "general": "general_agent"
    }
)

builder.add_edge("billing_agent", "quality_checker")
builder.add_edge("technical_agent", "quality_checker")
builder.add_edge("general_agent", "quality_checker")

builder.add_edge("quality_checker", "final_response")
builder.add_edge("final_response", END)

graph = builder.compile()

result = graph.invoke(
    {
        "query": "I made a payment but did not receive the invoice."
    }
)
print(result)