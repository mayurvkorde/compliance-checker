import argparse
import asyncio
import json
from typing import Dict
from app.graph import build_graph
from app.observability import build_observability, flush, resolve_trace_id
from data.regulations import REGULATIONS


async def run_compliance_check(regulation_id: str) -> Dict:
    if regulation_id not in REGULATIONS:
        raise SystemExit(
            f"Unknown regulation '{regulation_id}'. Options: {list(REGULATIONS)}"
        )
    regulation = REGULATIONS [regulation_id]

    #1. Observability: callbacks + a run id (root run id == LangSmith trace id).
    observability = build_observability()
    compiled_graph = build_graph()

    #2. Run the 2-step graph (async), traced with a clear name + tags + metadata
    # so the run is easy to find/screenshot in the LangSmith/Langfuse dashboard.

    graph_result = await compiled_graph.ainvoke(
        {"regulation_id": regulation_id, "regulation_text": regulation["mandate"]},
        config={
            "run_id": observability.run_id,
            "run_name": f"compliance-check:: {regulation_id}",
            "tags": ["compliance-checker", regulation_id],
            "metadata": {
                "regulation_id": regulation_id,
                "regulation_title": regulation["title"]
            }
        }
    )

    #3. Attach the trace id, flush the tracer.
    report = graph_result["report"]
    report["trace_id"] = resolve_trace_id(observability)
    flush (observability)

    return report

async def run_all() -> Dict:
    """Check every regulation concurrently and return a combined report.
    Each regulation is an independent, separately-traced run.
    """
    reports = list(
        await asyncio.gather(
            *(run_compliance_check(regulation_id) for regulation_id in REGULATIONS)
        )
    )
    return {
        "mode": "all",
        "checked": list(REGULATIONS),
        "conflicts_found": sum(1 for report in reports if report["conflict_detected"]),
        "reports": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated compliance checker")
    argument_group = parser.add_mutually_exclusive_group()
    argument_group.add_argument(
        "--regulation",
        default="REG_2026_PR_COMPLIANCE",
        help="Regulation id to check policies against.",
    )
    argument_group.add_argument(
        "--all",
        action="store_true",
        help="Check every regulation and emit a combined report.",
    )
    arguments = parser.parse_args()
    if arguments.all:
        output = asyncio.run(run_all())
    else:
        output = asyncio.run(run_compliance_check(arguments.regulation))
    print(json.dumps(output, indent=2))

if __name__=="__main__":
    main()