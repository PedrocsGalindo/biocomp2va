"""Construção de árvores didáticas para os exemplos do EvoRamos."""

from typing import Any

import networkx as nx

from src.distance import hamming_distance


def build_phylogenetic_tree(sequences: list[dict[str, Any]]) -> nx.Graph:
    """Mantém compatibilidade construindo uma árvore didática simples."""
    return _build_similarity_tree(sequences)


def build_example_graph(example: dict[str, Any]) -> nx.DiGraph:
    """Constrói o grafo de um exemplo e adiciona suas relações especiais."""
    graph = _build_similarity_tree(example["organisms"])

    expected_events_by_target = {
        (event["target_id"], event["target_type"]): event
        for event in example["expected_events"]
    }
    for node_id, attributes in graph.nodes(data=True):
        matched_event = expected_events_by_target.get((node_id, "node"))
        if matched_event:
            attributes["event_type"] = matched_event["event_type"]

    for edge in example["optional_edges"]:
        graph.add_edge(
            edge["source"],
            edge["target"],
            id=_build_edge_id(edge["source"], edge["target"]),
            event_type=edge["event_type"],
            is_special=True,
            label=edge.get("label", ""),
        )

    for source, target, attributes in graph.edges(data=True):
        attributes.setdefault("id", _build_edge_id(source, target))

    return graph


def _build_similarity_tree(sequences: list[dict[str, Any]]) -> nx.DiGraph:
    """Agrupa iterativamente os pares mais próximos em uma árvore binária."""
    graph = nx.DiGraph()
    clusters: list[dict[str, Any]] = []

    for organism in sequences:
        graph.add_node(
            organism["id"],
            label=organism["name"],
            sequence=organism["sequence"],
            type="organism",
            is_internal=False,
        )
        clusters.append({"node_id": organism["id"], "members": [organism]})

    ancestor_count = 1
    while len(clusters) > 1:
        left_index, right_index = _closest_cluster_pair(clusters)
        right = clusters.pop(right_index)
        left = clusters.pop(left_index)
        ancestor_id = f"ancestor_{ancestor_count}"
        ancestor_count += 1

        graph.add_node(
            ancestor_id,
            label=f"Ancestral {ancestor_count - 1}",
            type="ancestor",
            is_internal=True,
            event_type="divergence",
        )
        graph.add_edge(
            ancestor_id,
            left["node_id"],
            id=_build_edge_id(ancestor_id, left["node_id"]),
            event_type="normal",
            is_special=False,
            label="",
        )
        graph.add_edge(
            ancestor_id,
            right["node_id"],
            id=_build_edge_id(ancestor_id, right["node_id"]),
            event_type="normal",
            is_special=False,
            label="",
        )
        clusters.append(
            {"node_id": ancestor_id, "members": left["members"] + right["members"]}
        )

    return graph


def _closest_cluster_pair(clusters: list[dict[str, Any]]) -> tuple[int, int]:
    """Localiza o par de grupos com menor distância média."""
    best_pair = (0, 1)
    best_distance = float("inf")

    for left_index in range(len(clusters) - 1):
        for right_index in range(left_index + 1, len(clusters)):
            distance = _average_cluster_distance(
                clusters[left_index]["members"],
                clusters[right_index]["members"],
            )
            if distance < best_distance:
                best_distance = distance
                best_pair = (left_index, right_index)

    return best_pair


def _average_cluster_distance(
    left_members: list[dict[str, Any]],
    right_members: list[dict[str, Any]],
) -> float:
    """Calcula a distância média de Hamming entre dois grupos."""
    distances = [
        hamming_distance(left["sequence"], right["sequence"])
        for left in left_members
        for right in right_members
    ]
    return sum(distances) / len(distances)


def _build_edge_id(source: str, target: str) -> str:
    """Cria um identificador estável para arestas no Cytoscape."""
    return f"{source}__{target}"
