# The agent should:

# - Read incoming customer emails
# - Classify them by urgency and topic
# - Search relevant documentation to answer questions
# - Draft appropriate responses
# - Escalate complex issues to human agents
# - Schedule follow-ups when needed

# Example scenarios to handle:

# 1. Simple product question: "How do I reset my password?"
# 2. Bug report: "The export feature crashes when I select PDF format"
# 3. Urgent billing issue: "I was charged twice for my subscription!"
# 4. Feature request: "Can you add dark mode to the mobile app?"
# 5. Complex technical issue: "Our API integration fails intermittently with 504 errors"

from pathlib import Path

from langgraph.types import RetryPolicy
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from state.email_state import EmailAgentState
from nodes.email_nodes import (
    read_email, classify_intent, search_documentation,
    human_review, send_reply, bug_tracking, draft_response
)

def build_email_graph():
    workflow = StateGraph(EmailAgentState)
    workflow.add_node("read_email", read_email)
    workflow.add_node("classify_intent", classify_intent)
    # Add retry policy for nodes that might have transient failures
    workflow.add_node(
        "search_documentation",
        search_documentation,
        retry_policy=RetryPolicy(max_attempts=3)
    )

    workflow.add_node("human_review", human_review)
    workflow.add_node("bug_tracking", bug_tracking)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("send_reply", send_reply)

    # Add only the essential edges
    workflow.add_edge(START, "read_email")
    workflow.add_edge("read_email", "classify_intent")
    workflow.add_edge("send_reply", END)

    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    image = app.get_graph().draw_mermaid_png()
    Path(__file__).with_name("email_graph.png").write_bytes(image)
    return app
