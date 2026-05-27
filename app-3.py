from typing_extensions import TypedDict
from typing import Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# Define the state
class ChatState(TypedDict):
    user_message: str
    history: Annotated[list[str], operator.add]
    # operator.add: keeps on appending messages to the list so that we don't loose any message
    response: str

# Node to generate the response
def chatbot_node(state: ChatState):
    user_message = state['user_message']
    
    response = f"You said: {user_message}"
    return{
        "history": [f"User: {user_message}", f"Bot: {response}"],
        "response": response
    }

# Building the Graph
builder = StateGraph(ChatState)

builder.add_node("chatbot_node", chatbot_node)

builder.add_edge(START, "chatbot_node")
builder.add_edge("chatbot_node", END)


# Adding checkpointer
# Persists information in-memory
# for production, we don't use in-memory rather we persist perman
checkpointer = InMemorySaver()

graph = builder.compile(checkpointer=checkpointer)

# Use same Thread_id to preserve memory
config = {
    "configurable":{
        "thread_id": "user-1"
    }
}

result1 = graph.invoke(
    {
        "user_message": "Hi, my name is Arpita",
        "history": [],
        "response": ""
    },
    config = config
)

print("First response: ")
print(result1["response"])
print("History: ")
print(result1["history"])

result2 = graph.invoke(
    {
        "user_message": "What did I just say?",
        "history": [],
        "response": ""
    },
    config = config
)

print("\nSecond response: ")
print(result2["response"])
print("History: ")
print(result2["history"])