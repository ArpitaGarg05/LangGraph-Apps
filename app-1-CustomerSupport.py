from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

# define the state of the application
# TypedDict defines the structure of StateGraph
class SupportedState(TypedDict):
    user_query: str
    category: str
    answer: str

# Node-1
# user_query = when will I get my refund?
def classify_query(state: SupportedState):
    query = state["user_query"].lower()

    if "refund" in query:
        category = "refund"
    elif "return" in query or "returns" in query:
        category = "return"
    elif "shipping" in query or "delivery" in query or "delivered" in query:
        category = "delivery"
    else:
        category = "general"

    return {"category": category}

# Node-2
def answer_query(state: SupportedState):
    category = state["category"]
    query = state["user_query"]

    # here, we should call the LLM with RAG to answer the user query based on the company's knowledge base.
    answer = ""
    if category == "return":
        answer = "You can return the product within 7 days of delivery."
    elif category == "refund":
        answer = "Refund will br processed within 5-7 working days."
    elif category == "delivery":
        answer = "Orders are generally delivered within 3-5 days."
    else:
        answer = "For any other general query, please call our customer care."
    
    return {"answer": answer}

# Build the Graph
builder = StateGraph(SupportedState)

# add nodes
builder.add_node("classify_query", classify_query)
builder.add_node("answer_query", answer_query)

# add edges to decide the flow of execution
# add_Edge(x, y): x -> y
builder.add_edge(START, "classify_query")
builder.add_edge("classify_query", "answer_query")
builder.add_edge("answer_query", END)

graph = builder.compile()

# run the graph
result = graph.invoke(
    {
        "user_query": "When will my order be delivered",
        "category": "",
        "answer": ""
    }
)

print(result)