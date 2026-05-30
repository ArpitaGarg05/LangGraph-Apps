from typing import Literal
from state import SupportState

def classify_message(state: SupportState) -> SupportState:
    """
    Classifies the user's support message.
    
    In real production, this could be an llm call.
    For beginner-friendly teaching, we use simple keyword logic.
    """
    message = state['message'].lower()

    if any (word in message for word in ["charged", "payment", "refund", "invoice", "billing"]):
        return {
            "category": "billing",
            "risk": "high"
        }
    
    if any(word in message for word in ["crash", "bug", "error", "failed"]):
        