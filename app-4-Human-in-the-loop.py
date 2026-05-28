from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

# Define state
class RefundState(TypedDict):
    customer_name: str
    refund_amount: int
    approved: bool
    final_status: str

# Node: check if approval is needed
def check_refund_status(state: RefundState):
    amount = state["refund_amount"]

    if amount <= 1000:
        return{
            "approved": True,
            "final_status": "Small refund auto-approved."
        }
    return{
        "final_status": "large refund amount requires human approval."
    }

# Node: Human approval
def human_approval(state: RefundState):
    if state["refund_amount"] <= 1000:
        return {}
    # interrupt: pauses the function execution and wait for the human input
    # once the input is provided, it resumes the execution
    human_decision = interrupt({
        "message": "Approval required",
        "customer_name": state["customer_name"],
        "refund_amount": state["refund_amount"],
        "question": "Should we approve this refund?"
    })

    return{"approved": human_decision["approved"]}

# Node: Final processing
def process_refund(state: RefundState):
    if state["approved"]:
        return{
            "final_status": f"Refund of Rs{state['refund_amount']} has been approved."
        }
    return{
        "final_status": f"Refund of Rs{state['refund_amount']} has been rejected."
    }

# Build the graph
builder = StateGraph(RefundState)

builder.add_node("check_refund_status", check_refund_status)
builder.add_node("human_approval", human_approval)
builder.add_node("process_refund", process_refund)

builder.add_edge(START, "check_refund_status")
builder.add_edge("check_refund_status", "human_approval")
builder.add_edge("human_approval", "process_refund")
builder.add_edge("process_refund", END)

# Checkpointer to save the memory
checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

# Run graph
config = {
    "configurable": {
        "thread_id": "refund-request-101"
    }
}

first_result = graph.invoke(
    {
        "customer_name": "Arpita",
        "refund_amount": 5000,
        "approved": False,
        "final_status": ""
    },
    config=config
)

print("Graph paused for human approval.")
print(first_result)

# Command: Resume graph after human approval
final_result = graph.invoke(
    Command(resume={"approved": True}),
    config=config
)

print("\nFinal result:")
print(final_result["final_status"])