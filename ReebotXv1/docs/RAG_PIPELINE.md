# RAG Pipeline — RebootX

> Embedding strategy, chunking design, ChromaDB configuration, and retrieval logic.

---

## Overview

The RAG (Retrieval-Augmented Generation) pipeline is the core knowledge layer of RebootX. It provides contextual information to the LLM by retrieving relevant documents from a pre-built knowledge corpus based on the upgrade request.

```
Knowledge Corpus          Embedding Pipeline           Query Pipeline
(raw documents)           (offline / seed time)        (runtime / per-request)
      │                         │                            │
      ▼                         ▼                            ▼
┌──────────┐            ┌──────────────┐             ┌──────────────┐
│  Release  │           │  Text        │             │  Query       │
│  Notes    │──────────▶│  Chunking    │             │  Builder     │
│  Changelogs│          │  (~500 tokens)│             │  (from       │
│  CVE docs │           └──────┬───────┘             │  request)    │
│  Guides   │                  │                     └──────┬───────┘
└──────────┘                   ▼                            │
                        ┌──────────────┐                    │
                        │  Embed via   │                    ▼
                        │  nomic-embed │             ┌──────────────┐
                        │  -text       │             │  Embed query │
                        └──────┬───────┘             │  (same model)│
                               │                     └──────┬───────┘
                               ▼                            │
                        ┌──────────────┐                    │
                        │  ChromaDB    │◀───────────────────┘
                        │  Vector Store│   similarity search
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  Top-K       │
                        │  Results     │
                        │  + Metadata  │
                        └──────────────┘
```

---

## Knowledge Corpus

### Document Sources

| Source | Format | Example | Priority |
|--------|--------|---------|----------|
| Official Release Notes | HTML / Markdown | PostgreSQL 16 Release Notes | 🔴 Critical |
| Migration / Upgrade Guides | HTML / PDF | Python 3.12 What's New | 🔴 Critical |
| Deprecation Notices | Text / HTML | Django deprecation timeline | 🟠 High |
| Compatibility Matrices | Tables / JSON | psycopg2 PG version support | 🟠 High |
| CVE / Security Advisories | JSON (NVD) | CVE-2023-XXXX for PG 12 | 🟡 Medium |
| Community Runbooks | Markdown | "Upgrading PG 12 to 16 — lessons" | 🟡 Medium |
| Stack Overflow Answers | Text | Common upgrade issues | 🟢 Low |

### Corpus Organisation

```
app/knowledge/corpus/
├── database/
│   ├── postgresql/
│   │   ├── pg16-release-notes.md
│   │   ├── pg15-release-notes.md
│   │   ├── pg-upgrade-guide.md
│   │   └── psycopg2-compatibility.md
│   └── mysql/
│       └── ...
├── runtime/
│   ├── python/
│   │   ├── python-312-whatsnew.md
│   │   ├── python-311-whatsnew.md
│   │   ├── python-310-whatsnew.md
│   │   └── distutils-removal-pep632.md
│   └── java/
│       └── ...
├── mwaa/
│   ├── airflow-28-release-notes.md
│   ├── mwaa-supported-versions.md
│   └── provider-compatibility-matrix.md
└── emr/
    ├── emr-7x-release-notes.md
    └── spark-compatibility.md
```

---

## Chunking Strategy

### Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Chunk size** | 500 tokens (~2000 chars) | Balances context richness with embedding quality |
| **Chunk overlap** | 50 tokens (~200 chars) | Ensures continuity at chunk boundaries |
| **Splitter** | `RecursiveCharacterTextSplitter` (LangChain) | Respects document structure (headers, paragraphs, code blocks) |
| **Separators** | `["\n## ", "\n### ", "\n\n", "\n", ". ", " "]` | Splits at section headers first, then paragraphs, then sentences |

### Implementation

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000,           # characters (~500 tokens)
    chunk_overlap=200,          # characters (~50 tokens)
    separators=[
        "\n## ",               # H2 headers (highest priority split point)
        "\n### ",              # H3 headers
        "\n\n",                # Double newline (paragraph break)
        "\n",                  # Single newline
        ". ",                  # Sentence boundary
        " ",                   # Word boundary (last resort)
    ],
    length_function=len,
)

chunks = splitter.split_text(document_text)
```

### Metadata per Chunk

Each chunk is stored with the following metadata in ChromaDB:

```python
metadata = {
    "source": "pg16-release-notes.md",         # Source filename
    "technology_type": "Database",              # Database | Runtime | MWAA | EMR
    "technology_name": "PostgreSQL",            # Specific technology
    "version": "16",                            # Version this document covers
    "section": "Deprecated Features",           # Section header (if available)
    "doc_type": "release_notes",                # release_notes | migration_guide | cve | runbook
    "chunk_index": 3,                           # Position within the source document
    "total_chunks": 12,                         # Total chunks from this source
    "date": "2023-09-14",                       # Document date (if available)
}
```

---

## Embedding Model

### Model: `nomic-embed-text`

| Property | Value |
|----------|-------|
| **Model** | `nomic-embed-text` |
| **Provider** | Ollama (local) |
| **Dimensions** | 768 |
| **Max Tokens** | 8192 |
| **API** | `POST http://localhost:11434/api/embeddings` |

### Usage

```python
import requests

def embed_text(text: str) -> list[float]:
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text,
        }
    )
    return response.json()["embedding"]
```

### Why `nomic-embed-text`?

- Runs entirely through Ollama — no external API calls
- Good performance on retrieval benchmarks for its size
- Consistent with the "fully local" architecture principle
- 768-dimensional embeddings are efficient for ChromaDB storage

---

## ChromaDB Configuration

### Setup

```python
import chromadb

# Persistent storage (recommended for prototype)
client = chromadb.PersistentClient(path="./app/knowledge/embeddings")

# Create or get collection
collection = client.get_or_create_collection(
    name="rebootx_corpus",
    metadata={
        "hnsw:space": "cosine",        # Cosine similarity
        "hnsw:M": 16,                  # HNSW index parameter
        "hnsw:ef_construction": 200,   # Index build quality
    },
)
```

### Collection Schema

```
Collection: rebootx_corpus
├── IDs:        chunk unique identifiers (e.g., "pg16-release-notes-chunk-003")
├── Documents:  raw text chunks
├── Embeddings: 768-dim float vectors (nomic-embed-text)
└── Metadata:   structured metadata per chunk (see above)
```

### Indexing (Seed Script)

```python
def seed_corpus(corpus_dir: str):
    """Read all documents, chunk, embed, and store in ChromaDB."""
    for doc_path in Path(corpus_dir).rglob("*.md"):
        text = doc_path.read_text()
        metadata = extract_metadata(doc_path)
        chunks = splitter.split_text(text)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_path.stem}-chunk-{i:03d}"
            embedding = embed_text(chunk)

            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{**metadata, "chunk_index": i, "total_chunks": len(chunks)}],
            )
```

---

## Retrieval Strategy

### Query Building

The query is constructed from the upgrade request to maximise retrieval relevance:

```python
def build_query(request: UpgradeRequest) -> str:
    """Build a semantic search query from the upgrade request."""
    query_parts = [
        f"Upgrading {request.technology_type} from {request.current_version} to {request.target_version}",
        f"Breaking changes and compatibility issues",
        f"Dependencies: {', '.join(request.dependencies[:5])}",
        f"Integration risks with: {', '.join(request.integrations[:3])}",
    ]
    return " ".join(query_parts)
```

### Retrieval Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Top-K** | 8 | Balance between context richness and prompt size |
| **Distance metric** | Cosine similarity | Standard for text embeddings |
| **Metadata filter** | `technology_type` match | Reduces noise from unrelated technologies |
| **Score threshold** | 0.65 | Filter out low-relevance results |

### Retrieval Implementation

```python
def retrieve_context(request: UpgradeRequest, top_k: int = 8) -> list[dict]:
    """Retrieve relevant documents from ChromaDB."""
    query_text = build_query(request)
    query_embedding = embed_text(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"technology_type": request.technology_type.value},
        include=["documents", "metadatas", "distances"],
    )

    # Filter by score threshold and deduplicate
    context_chunks = []
    seen_sources = set()

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist > 0.35:  # cosine distance > 0.35 means similarity < 0.65
            continue
        source_key = (meta["source"], meta.get("section", ""))
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            context_chunks.append({
                "text": doc,
                "source": meta["source"],
                "section": meta.get("section", ""),
                "relevance_score": 1 - dist,
            })

    return context_chunks
```

---

## Context Assembly

Retrieved chunks are formatted for injection into the LLM prompt:

```python
def assemble_context(chunks: list[dict]) -> str:
    """Format retrieved chunks for the LLM prompt."""
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"--- Source {i}: {chunk['source']} ({chunk['section']}) "
            f"[relevance: {chunk['relevance_score']:.2f}] ---\n"
            f"{chunk['text']}\n"
        )
    return "\n".join(context_parts)
```

---

## Evaluation & Tuning

### Metrics to Track

| Metric | Target | How to Measure |
|--------|--------|----------------|
| **Retrieval Precision** | > 70% | Of the top-K results, how many are actually relevant? |
| **Retrieval Recall** | > 80% | Of all relevant docs, how many appear in top-K? |
| **Chunk Utilisation** | > 60% | What % of retrieved chunks does the LLM actually reference? |
| **Embedding Latency** | < 100ms/chunk | Time to embed a single chunk via Ollama |
| **Query Latency** | < 200ms | Time for ChromaDB similarity search |

### Tuning Knobs

| Knob | Effect | Trade-off |
|------|--------|-----------|
| Increase chunk size | More context per chunk | Fewer chunks fit in prompt |
| Increase top-K | More diverse context | More noise, longer prompts |
| Add metadata filters | Higher precision | May miss cross-technology risks |
| Lower score threshold | More results | More irrelevant context |
| Multi-query retrieval | Better recall | Higher latency |
