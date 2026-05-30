from typing_extensions import TypedDict

class SupportState(TypedDict, total = False):
    user_id: str
    message: str

    category: str
    risk: str

    policy_text: str
    draft_response: str
    escalation_reason: str

    final_response: str