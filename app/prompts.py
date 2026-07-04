from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.schemas import PolicyVerdict

verdict_parser = PydanticOutputParser(pydantic_object=PolicyVerdict)

_SYSTEM_TEMPLATE = """
You are a strict corporate compliance Auditor. Decide whether ONE company
policy VIOLETS ONE regulation.

Rules:
- A policy violates the regulation if it PERMITS or omits something the regulation 
  now MANDATES or forbids (e.g., allowing an action without a control the regulation 
  requires).
- If the policy is about an unrelated topic, it does NOT violate the regulation.
- Be specific: cite what the policy allows vs. what the regulation requires.
- If it violates, give a concrete recommended_action to amend the policy.
{format_instructions}"""

_HUMAN_TEMPLATE = """REGULATION ({regulation_id}):
{regulation_text}
COMPANY POLICY ({policy_id} - {policy_section}):
{policy_text}
Evaluate whether this policy violates the regulation."""

AUDITOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_TEMPLATE),
        ("human", _HUMAN_TEMPLATE),
    ]
).partial(format_instructions=verdict_parser.get_format_instructions())

def build_auditor_chain(llm):
    return AUDITOR_PROMPT | llm | verdict_parser