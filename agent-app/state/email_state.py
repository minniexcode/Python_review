from typing import TypedDict, Literal


# Define the structure for email classification
class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str

class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str
    # The classification can be None if the email has not been classified yet
    classification: EmailClassification | None

    # Raw search/API results
    search_results: list[str] | None
    customer_history: dict | None

    # Generated content
    draft_response: str | None
    messages: list[str] | None
