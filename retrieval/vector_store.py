"""Embed chunks and store them in a persistent ChromaDB collection."""

import re
from pathlib import Path
from typing import Dict, List, Optional

import chromadb
from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions

from chunking import chunk_documents
from ingestion.ingest_all import ingest_all

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DEFAULT_PERSIST_DIR = "chroma_db"
DEFAULT_COLLECTION = "unofficial_guide"
DEFAULT_TOP_K = 4
COURSE_CODE_PATTERN = re.compile(
    r"\b(COP|CDA|CIS|MAC|MAD|CGS|CEN|CNT|CAP)\s*(\d{4})\b",
    re.IGNORECASE,
)


def _embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )


def get_client(persist_dir: str = DEFAULT_PERSIST_DIR) -> chromadb.PersistentClient:
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_collection(
    persist_dir: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
):
    client = get_client(persist_dir)
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def build_index(
    chunks: Optional[List[Dict]] = None,
    *,
    persist_dir: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
    reset: bool = False,
) -> chromadb.Collection:
    """
    Embed chunks and store them in ChromaDB.

    If chunks is None, runs ingest_all() and chunk_documents().
    When reset=False and the collection already has data, returns it as-is.
    """
    if chunks is None:
        chunks = chunk_documents(ingest_all())

    client = get_client(persist_dir)

    if reset:
        try:
            client.delete_collection(collection_name)
        except NotFoundError:
            pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )

    if not reset and collection.count() > 0:
        return collection

    ids = [f"chunk_{index:04d}" for index in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection


def _expand_neighbor_chunks(
    collection: chromadb.Collection,
    hits: List[Dict],
    *,
    window: int = 1,
    max_total: int = 8,
    expand_top_n: int = 2,
) -> List[Dict]:
    """
    When a split document matches, also pull nearby chunks from the same file.

    Neighbors are inserted right after the matching hit so context stays together.
    """
    if window <= 0:
        return hits[:max_total]

    expanded: List[Dict] = []
    seen_ids = {hit["id"] for hit in hits}
    file_cache: Dict[str, Dict[int, Dict]] = {}

    def chunks_for_file(file_path: str) -> Dict[int, Dict]:
        if file_path in file_cache:
            return file_cache[file_path]

        result = collection.get(
            where={"file": file_path},
            include=["documents", "metadatas"],
        )
        by_index = {}
        for doc_id, text, metadata in zip(
            result["ids"],
            result["documents"],
            result["metadatas"],
        ):
            index = metadata.get("chunk_index", metadata.get("sectionIndex", 0))
            by_index[index] = {
                "id": doc_id,
                "text": text,
                "metadata": metadata,
                "distance": None,
            }
        file_cache[file_path] = by_index
        return by_index

    for rank, hit in enumerate(hits):
        expanded.append(hit)

        if rank >= expand_top_n or len(expanded) >= max_total:
            continue

        meta = hit["metadata"]
        chunk_total = meta.get("chunk_total", meta.get("sectionTotal", 1))
        if chunk_total <= 1:
            continue

        file_path = meta.get("file")
        if not file_path:
            continue

        chunk_index = meta.get("chunk_index", meta.get("sectionIndex", 0))
        by_index = chunks_for_file(file_path)
        start = max(0, chunk_index - window)
        end = min(chunk_total, chunk_index + window + 1)

        for index in range(start, end):
            if index == chunk_index or len(expanded) >= max_total:
                continue
            neighbor = by_index.get(index)
            if neighbor and neighbor["id"] not in seen_ids:
                expanded.append(neighbor)
                seen_ids.add(neighbor["id"])

    return expanded[:max_total]


def _course_file_tags(query: str) -> List[str]:
    """Map course codes in a query to filename stems like cop3514."""
    tags = []
    for dept, number in COURSE_CODE_PATTERN.findall(query):
        tags.append(f"{dept.lower()}{number}")
    return tags


def _boost_course_file_matches(
    collection: chromadb.Collection,
    query: str,
    hits: List[Dict],
    *,
    max_boost: int = 4,
) -> List[Dict]:
    """Pull in top chunks from files named after course codes mentioned in the query."""
    file_tags = _course_file_tags(query)
    if not file_tags:
        return hits

    seen_ids = {hit["id"] for hit in hits}
    all_docs = collection.get(include=["metadatas"])
    reddit_ids = []
    other_ids = []

    for doc_id, metadata in zip(all_docs["ids"], all_docs["metadatas"]):
        if doc_id in seen_ids:
            continue
        if (metadata.get("section") or "").startswith("POST"):
            continue

        file_path = (metadata.get("file") or "").lower()
        if not any(tag in file_path for tag in file_tags):
            continue

        if any(file_path.endswith(f"reddit_{tag}.txt") for tag in file_tags):
            reddit_ids.append(doc_id)
        else:
            other_ids.append(doc_id)

    candidate_ids = reddit_ids if reddit_ids else other_ids
    if not candidate_ids:
        return hits

    result = collection.query(
        query_texts=[query],
        n_results=min(max_boost, len(candidate_ids)),
        ids=candidate_ids,
    )

    boosted: List[Dict] = []
    for index in range(len(result["ids"][0])):
        boosted.append({
            "id": result["ids"][0][index],
            "text": result["documents"][0][index],
            "metadata": result["metadatas"][0][index],
            "distance": result["distances"][0][index],
        })

    return boosted + hits


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    *,
    collection: Optional[chromadb.Collection] = None,
    persist_dir: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION,
    expand_neighbors: int = 2,
    max_chunks: int = 8,
) -> List[Dict]:
    """Return the top-k most similar chunks for a query."""
    if collection is None:
        collection = get_collection(persist_dir, collection_name)

    results = collection.query(query_texts=[query], n_results=top_k)

    chunks: List[Dict] = []
    for index in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][index],
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index],
        })

    chunks = _boost_course_file_matches(collection, query, chunks)
    return _expand_neighbor_chunks(
        collection,
        chunks,
        window=expand_neighbors,
        max_total=max_chunks,
    )
