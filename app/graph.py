from typing import Dict, List, TypedDict
from langgraph.graph import END, START, StateGraph
from app.llm import get_llm
from app.report import assemble_report
from app.schemas import PolicyVerdict, PolicyState
from app.vectorstore import retrieve_policies
import asyncio
from app.prompts import build_auditor_chain

_audit_semaphore = asyncio.Semaphore(5)

class AuditState(TypedDict, total=False):
    regulation_id: str
    regulation_text: str
    retrieved_policies: List[Dict]
    policy_verdicts: List[PolicyState]
    report: Dict

def retrieve_node(state: AuditState) -> Dict:
    """Retrieve the policies most relevant to the regulation."""
    top_k = 3
    retrieved_policies = retrieve_policies(state["regulation_text"], top_k=top_k)
    return {"retrieved_policies": retrieved_policies}


async def audit_one_policy(
    auditor_chain, regulation_id: str, regulation_text: str, policy: Dict
) -> Dict:
    """Audit a single policy against the regulation (bounded by the semaphore)."""
    async with _audit_semaphore:
        verdict: PolicyVerdict = await auditor_chain.ainvoke(
            {
                "regulation_id":regulation_id,
                "regulation_text":regulation_text,
                "policy_id":policy["policy_id"],
                "policy_section":policy.get("section"),
                "policy_text":policy["text"],
            }
        )
    return {
        "policy_id": policy ["policy_id"],
        "violates": verdict.violates,
        "reason": verdict.reason,
        "recommended_action": verdict.recommended_action
    }


async def audit_node(state: AuditState) -> Dict:
    """Auditor: structured verdict per policy (run concurrently), then assemble.
    The per-policy audits are independent, so they run in parallel (bounded by ``_audit_semaphore to respect LLM rate limits).
    """
    auditor_chain = build_auditor_chain(get_llm())

    policy_verdicts: List[Dict] = list(
        await asyncio.gather(
            *(
                audit_one_policy(
                    auditor_chain,
                    state["regulation_id"],
                    state["regulation_text"],
                    policy,
                )
                for policy in state["retrieved_policies"]
            )
        )
    )
    report = assemble_report(state["regulation_id"], policy_verdicts)

    return {"policy_verdicts": policy_verdicts, "report": report.model_dump()}


def build_graph():
    """Compile the retrieve -> audit graph."""
    graph = StateGraph (AuditState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("audit", audit_node)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "audit")
    graph.add_edge("audit", END)
    return graph.compile()