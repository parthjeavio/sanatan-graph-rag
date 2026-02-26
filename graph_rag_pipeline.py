import argparse
import json
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from sanatan_scraper import MythologyScraper


ENTITY_TYPES = [
    "Deity",
    "Avatar",
    "Asura/Rakshasa",
    "Human/Warrior",
    "Sage/Rishi",
    "Astra/Weapon",
    "Location",
]

RELATION_TYPES = [
    "AVATAR_OF",
    "CURSED_BY",
    "KILLED_BY",
    "WIELDS",
    "FATHER_OF",
    "MOTHER_OF",
    "MARRIED_TO",
    "SIBLING_OF",
]

ENTITY_LEXICON = {
    "Vishnu": "Deity",
    "Shiva": "Deity",
    "Saraswati": "Deity",
    "Rama": "Avatar",
    "Krishna": "Avatar",
    "Narasimha": "Avatar",
    "Ravana": "Asura/Rakshasa",
    "Hiranyakashipu": "Asura/Rakshasa",
    "Hiranyaksha": "Asura/Rakshasa",
    "Kumbhakarna": "Asura/Rakshasa",
    "Arjuna": "Human/Warrior",
    "Bhishma": "Human/Warrior",
    "Durvasa": "Sage/Rishi",
    "Vishwamitra": "Sage/Rishi",
    "Brahmastra": "Astra/Weapon",
    "Sudarshana Chakra": "Astra/Weapon",
    "Gandiva": "Astra/Weapon",
    "Ayodhya": "Location",
    "Lanka": "Location",
    "Kurukshetra": "Location",
}

PATTERNS = [
    ("AVATAR_OF", re.compile(r"\b([A-Z][a-z]+)\b\s+(?:is|was)\s+(?:an\s+)?avatar of\s+\b([A-Z][a-z]+)\b", re.I)),
    ("CURSED_BY", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+(?:was\s+)?cursed by\s+\b([A-Z][A-Za-z]+)\b", re.I)),
    ("KILLED_BY", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+(?:was\s+)?killed by\s+\b([A-Z][A-Za-z]+)\b", re.I)),
    ("WIELDS", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+(?:wields?|wielded)\s+\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\b", re.I)),
    ("FATHER_OF", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+is\s+the\s+father of\s+\b([A-Z][A-Za-z]+)\b", re.I)),
    ("MOTHER_OF", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+is\s+the\s+mother of\s+\b([A-Z][A-Za-z]+)\b", re.I)),
    ("MARRIED_TO", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+(?:is|was)\s+married to\s+\b([A-Z][A-Za-z]+)\b", re.I)),
    ("SIBLING_OF", re.compile(r"\b([A-Z][A-Za-z]+)\b\s+(?:is|was)\s+(?:the\s+)?(?:brother|sister) of\s+\b([A-Z][A-Za-z]+)\b", re.I)),
]


@dataclass
class Node:
    id: str
    type: str


@dataclass
class Edge:
    source: str
    relation: str
    target: str


class MythGraph:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []
        self.adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)

    def add_node(self, name: str, node_type: str = "Unknown") -> None:
        if name not in self.nodes:
            self.nodes[name] = Node(id=name, type=node_type)

    def add_edge(self, source: str, relation: str, target: str) -> None:
        self.add_node(source, ENTITY_LEXICON.get(source, "Unknown"))
        self.add_node(target, ENTITY_LEXICON.get(target, "Unknown"))
        edge = Edge(source=source, relation=relation, target=target)
        if edge not in self.edges:
            self.edges.append(edge)
            self.adjacency[source].append((relation, target))

        if relation in {"SIBLING_OF", "MARRIED_TO"}:
            reverse = Edge(source=target, relation=relation, target=source)
            if reverse not in self.edges:
                self.edges.append(reverse)
                self.adjacency[target].append((relation, source))

    def to_dict(self) -> dict:
        return {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edges],
        }

    def answer_killer_of_sibling_demon(self, entity_name: str) -> str:
        sibling = self._traverse(entity_name, "SIBLING_OF")
        if not sibling:
            return f"No sibling relationship found for {entity_name}."

        killed_by = self._traverse(sibling, "KILLED_BY")
        if not killed_by:
            return f"Found sibling {sibling}, but no KILLED_BY relationship for them."

        avatar_of = self._traverse(killed_by, "AVATAR_OF")
        if avatar_of:
            return (
                f"The demon who was the sibling of {entity_name} is {sibling}. "
                f"{sibling} was killed by {killed_by}, who is an avatar of {avatar_of}."
            )
        return f"The demon who was the sibling of {entity_name} is {sibling}, and they were killed by {killed_by}."

    def _traverse(self, source: str, relation: str) -> str | None:
        for rel, target in self.adjacency.get(source, []):
            if rel == relation:
                return target
        return None


class GraphBuilder:
    def __init__(self):
        self.graph = MythGraph()

    def extract(self, documents: Iterable[str]) -> MythGraph:
        for text in documents:
            self._extract_entities(text)
            self._extract_relations(text)
        return self.graph

    def _extract_entities(self, text: str) -> None:
        for entity, entity_type in ENTITY_LEXICON.items():
            if re.search(rf"\b{re.escape(entity)}\b", text):
                self.graph.add_node(entity, entity_type)

    def _extract_relations(self, text: str) -> None:
        for relation, pattern in PATTERNS:
            for match in pattern.finditer(text):
                source = self._normalize_entity(match.group(1))
                target = self._normalize_entity(match.group(2))
                self.graph.add_edge(source, relation, target)

    def _normalize_entity(self, name: str) -> str:
        name = name.strip()
        if name in ENTITY_LEXICON:
            return name
        for known in ENTITY_LEXICON:
            if known.lower() == name.lower():
                return known
        return name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Hindu mythology graph from scraped text.")
    parser.add_argument(
        "--urls",
        nargs="+",
        default=[],
        help="Source URLs to scrape (Wikipedia, sacred-texts, blogs/wikis).",
    )
    parser.add_argument(
        "--text-files",
        nargs="+",
        default=[],
        help="Optional local text files to ingest when network scraping is unavailable.",
    )
    parser.add_argument(
        "--graph-output",
        default="mythology_graph.json",
        help="Path to write graph JSON output.",
    )
    parser.add_argument(
        "--question-entity",
        default="Hiranyaksha",
        help="Entity used for sample query: 'Who killed the demon that was the brother of <entity>?'.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scraper = MythologyScraper()

    documents = scraper.scrape(args.urls) if args.urls else []

    local_texts = []
    for file_path in args.text_files:
        local_texts.append(Path(file_path).read_text(encoding="utf-8"))

    extracted_texts = [doc.text for doc in documents] + local_texts
    if not extracted_texts:
        raise SystemExit("No input text found. Provide --urls and/or --text-files.")

    builder = GraphBuilder()
    graph = builder.extract(extracted_texts)

    output_path = Path(args.graph_output)
    output_path.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")

    print(f"Saved graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges to {output_path}.")
    print(graph.answer_killer_of_sibling_demon(args.question_entity))


if __name__ == "__main__":
    main()
