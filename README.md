# Sanatan Graph RAG (Starter)

This project builds a **Graph RAG-friendly mythology knowledge graph** from scraped text sources such as:

- Sacred-texts pages
- Wikipedia pages
- Mythology blogs/wikis

## Ontology (Graph Rules)

### Node types
- Deity
- Avatar
- Asura/Rakshasa
- Human/Warrior
- Sage/Rishi
- Astra/Weapon
- Location

### Edge types
- AVATAR_OF
- CURSED_BY
- KILLED_BY
- WIELDS
- FATHER_OF
- MOTHER_OF
- MARRIED_TO
- SIBLING_OF

## What is implemented

1. `sanatan_scraper.py`
   - Scrapes text from URLs.
   - Uses the Wikipedia API when applicable for cleaner extraction.
   - Falls back to generic HTML paragraph extraction.

2. `graph_rag_pipeline.py`
   - Applies ontology-driven extraction over scraped text.
   - Builds an in-memory graph of nodes and edges.
   - Exports the graph to JSON.
   - Runs a sample graph query:
     - "Who killed the demon that was the brother of Hiranyaksha?"

## Run

```bash
# Online mode
python graph_rag_pipeline.py \
  --urls \
    "https://en.wikipedia.org/wiki/Hiranyakashipu" \
    "https://en.wikipedia.org/wiki/Narasimha" \
    "https://en.wikipedia.org/wiki/Hiranyaksha" \
  --graph-output mythology_graph.json \
  --question-entity Hiranyaksha

# Offline fallback mode
python graph_rag_pipeline.py \
  --text-files examples/sample_corpus.txt \
  --graph-output mythology_graph.json \
  --question-entity Hiranyaksha
```


## Chatbot UI

A simple browser-based chatbot UI is included for question answering over extracted graph relations.

```bash
python -m http.server 8000
# then open http://localhost:8000/chatbot_ui.html
```

### What the UI currently provides

- Paste/edit corpus text and rebuild the graph instantly.
- Chat interface for relation-style questions (currently supports the sibling/killed-by pattern).
- A graph snapshot panel with node/edge tables and JSON export.

### Visualization roadmap

The UI includes a concrete visualization plan:

1. Entity Overview (node type counts).
2. Relation Distribution (edge type counts).
3. Interactive Graph View (force-directed network).
4. Path Explorer (multi-hop traversal between selected entities).
5. Source Traceability (edge-level supporting snippets).

## Next steps

- Replace regex extraction with an LLM-based extractor constrained by the same ontology.
- Insert graph output into Neo4j.
- Add Cypher-based multi-hop retrieval in place of the current in-memory traversal.
- Add source provenance per edge (`source_url`, sentence offsets).
