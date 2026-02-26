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

## Next steps

- Replace regex extraction with an LLM-based extractor constrained by the same ontology.
- Insert graph output into Neo4j.
- Add Cypher-based multi-hop retrieval in place of the current in-memory traversal.
- Add source provenance per edge (`source_url`, sentence offsets).
