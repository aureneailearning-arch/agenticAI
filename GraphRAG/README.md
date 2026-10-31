# GraphRAG Demo: Neo4j + LangChain + Gemini

A small classroom demo that turns two text files into a knowledge graph in Neo4j,
then answers questions about them by having an LLM write Cypher queries.

## What it shows

```
Text files ──► Chunks ──► Gemini extracts ──► GraphDocuments ──► Neo4j
                          entities + relations   (Python objects)   (stored via Cypher MERGE)

Question ──► Gemini writes Cypher ──► Neo4j runs it ──► Gemini writes the answer
```

| Step | Who does it | Output |
|------|-------------|--------|
| Extract | LLM (Gemini) | Nodes and relationships as structured data |
| GraphDocument | LangChain code | Python objects (nodes, relationships, source chunk) |
| Store | `Neo4jGraph.add_graph_documents` | Cypher `MERGE` run in Neo4j |
| Query | LLM via `GraphCypherQAChain` | Cypher `MATCH` query, then a plain-English answer |

## Files

| File | Purpose |
|------|---------|
| `GraphRAG_Neo4j_Gemini_Demo.ipynb` | The step-by-step notebook |
| `requirements.txt` | Python packages |
| `data/team.txt`, `data/projects.txt` | Sample inputs (created by the notebook) |

## Prerequisites

1. **Python 3.10+**
2. **Neo4j running locally**: Neo4j Desktop or Docker, reachable at `bolt://localhost:7687`.
3. **APOC plugin** enabled on that database. LangChain uses it to read the graph schema.
   - Neo4j Desktop: open your database → *Plugins* → install **APOC** → restart.
   - Docker:
     ```bash
     docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
       -e NEO4J_AUTH=neo4j/password123 \
       -e NEO4J_PLUGINS='["apoc"]' \
       neo4j:latest
     ```
4. **Google AI Studio API key** (free tier is enough): https://aistudio.google.com/apikey

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook GraphRAG_Neo4j_Gemini_Demo.ipynb
```

In the **Step 1 · Settings** cell, set:

```python
NEO4J_PASSWORD = "your_password_here"   # your Neo4j password
GEMINI_MODEL = "gemini-3.6-flash"       # any free-tier Gemini model shown in AI Studio
```

Create a `.env` file next to the notebook from `.env.example` and add your Google AI Studio API key:

```dotenv
GOOGLE_API_KEY=your-google-ai-studio-api-key
```

The notebook loads the key from `.env` using `python-dotenv`. Keep `.env` private; it is ignored by Git.

## Run it

Run the cells top to bottom:

1. Install packages (skip if you used `requirements.txt`)
2. Settings
3. Create the two text files
4. Load and chunk them
5. Connect to Neo4j and Gemini (**clears the database** so the demo can be re-run)
6. Extract entities and relationships, and print them
7. Store the graph in Neo4j
8. Ask questions; the generated Cypher is printed for each one

To see the graph, open Neo4j Browser at http://localhost:7474 and run:

```cypher
MATCH (n) RETURN n
```

## Sample questions

- Where does Alice work?
- Who studied at IIT Hyderabad?
- In which cities does Google have offices?
- Which company has an office in the city where Alice lives? *(two hops)*

## Troubleshooting

| Problem | Fix |
|---------|-----|
| APOC / `apoc.meta.data` error | Install the APOC plugin and restart the database |
| `ServiceUnavailable` / connection refused | Make sure Neo4j is running and the URI/port are correct |
| Authentication failure | Check `NEO4J_USERNAME` / `NEO4J_PASSWORD` |
| `429` / quota exceeded | Free-tier rate limit; wait a minute and re-run the cell |
| Model not found | Change `GEMINI_MODEL` to a model listed in AI Studio for your key |
| Empty or wrong answer | Look at the printed Cypher; node names must match what the extraction step printed |

## Notes

- `allow_dangerous_requests=True` is required because the LLM runs queries on your database.
  For anything beyond a local demo, connect the query chain with a **read-only** Neo4j user.
- This demo uses only the graph, no embeddings. A natural next step is hybrid retrieval:
  add a vector index on the `Document` (chunk) nodes and combine it with graph traversal.


env example 

GOOGLE_API_KEY=
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=Sample@123
GEMINI_MODEL=gemini-3.5-flash-lite