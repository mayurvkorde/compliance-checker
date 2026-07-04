from typing import Dict, List
import chromadb
from data.policies import POLICIES

_COLLECTION_NAME = "company_policies"

_chroma_client = chromadb.EphemeralClient()

def get_collection():
    """Return the policies collection, seeding (ingesting) it on first use."""
    collection = _chroma_client.get_or_create_collection(name=_COLLECTION_NAME)
    if collection.count() == 0:
        collection.add(
            ids=[policy["id"] for policy in POLICIES],
            documents=[policy ["text"] for policy in POLICIES],
            metadatas=[
                {"section": policy["section"], "policy_id": policy["id"]}
                for policy in POLICIES
            ]
        )
    return collection

def retrieve_policies (query_text: str, top_k: int) -> List[Dict]:
    """Semantic search: return the top-k policies most relevant to `query_text`."""
    collection = get_collection()
    result_count = min(top_k, collection.count())
    query_result = collection.query(query_texts=[query_text], n_results=result_count)
    policy_ids = query_result["ids"] [0]
    documents = query_result["documents"] [0]
    metadatas = query_result["metadatas"] [0]
    distances = query_result.get("distances", [[None] * len(policy_ids)])[0]
    return [
        {
        "policy_id": policy_id,
        "section": (metadata or {}).get("section"),
        "text": document,
        "distance": distance,
        }
        for policy_id, document, metadata, distance in zip(
            policy_ids, documents, metadatas, distances
        )
    ]