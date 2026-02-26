# Setup Guide

This project has:
- **Backend (Python Graph RAG pipeline):** `graph_rag_pipeline.py`
- **Frontend (browser UI):** `chatbot_ui.html` served as a static file

## 1) Prerequisites

- Python **3.10+**
- `pip` (usually included with Python)

Check your Python version:

```bash
python --version
```

## 2) Clone and enter the project

```bash
git clone <your-repo-url>
cd sanatan-graph-rag
```

## 3) (Recommended) Create a virtual environment

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 4) Backend: run the graph pipeline

This repository uses only Python standard-library modules, so no package install is required.

### Option A: Offline mode (works without internet)

```bash
python graph_rag_pipeline.py \
  --text-files examples/sample_corpus.txt \
  --graph-output mythology_graph.json \
  --question-entity Hiranyaksha
```

### Option B: Online mode (scrape source URLs)

```bash
python graph_rag_pipeline.py \
  --urls \
    "https://en.wikipedia.org/wiki/Hiranyakashipu" \
    "https://en.wikipedia.org/wiki/Narasimha" \
    "https://en.wikipedia.org/wiki/Hiranyaksha" \
  --graph-output mythology_graph.json \
  --question-entity Hiranyaksha
```

Expected result:
- Console prints graph stats and a sample answer.
- `mythology_graph.json` is generated in the project root.

## 5) Frontend: start the chatbot UI

In a **separate terminal** (same repo folder):

```bash
python -m http.server 8000
```

Then open:

- `http://localhost:8000/chatbot_ui.html`

## 6) Suggested local workflow

1. Start the frontend server (`python -m http.server 8000`).
2. Open the chatbot UI in browser.
3. Run backend pipeline commands when you want fresh extracted graph output.
4. Use UI to paste corpus text, rebuild graph, and ask questions.

## 7) Troubleshooting

- **`python: command not found`**
  - Try `python3` instead of `python`.
- **Port 8000 already in use**
  - Start server on another port:
  ```bash
  python -m http.server 8080
  ```
  - Then open `http://localhost:8080/chatbot_ui.html`.
- **No data extracted in online mode**
  - Check network connectivity.
  - Retry using offline mode with `examples/sample_corpus.txt`.
