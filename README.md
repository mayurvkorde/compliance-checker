# Automated Compliance Checker

Checks whether internal *company policies* violate a *new regulation, using a 2-step **LangGraph* workflow, an in-memory *ChromaDB* vector store, an *LLM auditor, and **Langfuse* tracing. Outputs a structured JSON report with a trace_id`.

## How it works

1. *Retrieve* find the policies relevant to the regulation (ChromaDB).
2. *Audit* an LLM checks each policy and returns {violates, reason, recommended_action}.
3. *Report* the verdicts are combined into structured JSON (with the trace_id`).

```
regulation -> [retrieve: ChromaDB] -> [audit: LLM] ->  ComplianceReport (JSON + trace_id)
```

## Setup

```
bash
cd compliance-checker
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
```

## Run

```
bash
python main.py --regulation REG_2026_PR_COMPLIANCE
python main.py --regulation REG_2026_SEC_VENDOR
python main.py --all
```

## Example output
```
json
{
    "target_regulation": "REG_2026_PR_COMPLIANCE",
    "conflict_detected": true,
    "conflicting_policies": [
        { 
            "policy_id": "policy_001", 
            "reason": "Policy 001 allows public project updates without pre-approval,
            contradicting the regulation's mandate for documented PR Committee sign-off."
        }
    ],
    "recommended_action": "Update Policy 001 to require documented PR Compliance Committee sign-off before any public/social-media project update.",
    "trace_id": "6f1c2e5a-..."
}
```


## Test

```
bash
pytest
```


## Notes

- **Retrieval is free* ChromaDB uses local embeddings (no API key). Only the auditor LLM needs a key.
- **LLM_MODEL* supports 'openai:...' via LangChain.

## Project layout
```
main.py                         entrypoint (run one regulation or --all)
config/settings.py              configuration (.env)
data/                           policies.py, regulations.py (sample data)
app/vectorstore.py              ChromaDB store (ingest + retrieve)
app/graph.py                    LangGraph: retrieve -> audit
app/schemas.py                  Pydantic models (PolicyVerdict, ComplianceReport)
app/report.py                   builds the final report
app/observability.py            Langfuse tracing trace_id
```
