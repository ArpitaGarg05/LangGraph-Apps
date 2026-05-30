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
        return {
            "category": "technical",
            "risk": "medium"
        }
    
    return {
        "category": "general",
        "risk": "low"
    }

def route_after_classification(state: SupportState) -> Literal["escalate", "answer"]:
    """
    Decides which path the graph should take.
    """

    if state["category"] == "billing" and state["risk"] == "high":
        return "escalate"
    
    return "answer"

def retrieve_policy(state: SupportState) -> SupportState:
    """
    Retrieves policy text based on category.
    
    In real production, this could call:
    -vector database
    -internal knowledge base
    -SQL database
    -search service
    """

    category = state["category"]

    policies = {
        "technical": "For technical issues, ask the user for logs, screenshots, and steps to reproduce.",
        "billing": "For billing issues, verify invoice ID and payment status before taking the action.",
        "general": "For general questions, provide a clear answer and ask if they need more help."
    }

    return {
        "policy_text": policies.get(category, policies["general"])
    }

def draft_response(state: SupportState) -> SupportState:
    """
    Creates a final support response.
    """
    message = state["message"]
    policy = state["policy_text"]

    response = (
        "Thanks for reaching out."
        f"Based on your message: '{message}', here is the recommended next step."
        f"{policy}"
    )

    return {
        "draft_response": response,
        "final_response": response
    }

def escalate_to_human(state: SupportState) -> SupportState:
    """
    Escalates risky billing issues to a human support team.
    
    In real production this node could create a Zendesk/Jira/Freshdesk ticket.
    """

    reason = (
        f"Billing-sensitive issue detected for user_id = {state["user_id"]}"
        "Human review is required before sending a final answer."
    )

    return {
        "escalation_reason": reason,
        "final_response": (
            "Your request involves billing/payment details."
            "I have escalated this to our support team for manual review."
        )
    }