"""Construção de árvores didáticas para os exemplos do EvoRamos.

A árvore principal agora é construída por uma implementação didática inspirada
no UPGMA. O objetivo é ser tecnicamente mais honesto que o agrupamento por
similaridade direta, mas ainda simples o suficiente para um MVP educacional.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import networkx as nx

from src.distance import aligned_sequence_distance, build_distance_matrix


@dataclass
class Cluster:
    """Representa um cluster ativo durante o UPGMA."""

    node_id: str
    label: str
    members: list[dict[str, Any]]
    height: float = 0.0
    children: tuple["Cluster", "Cluster"] | None = None
    size: int = field(init=False)

    def __post_init__(self) -> None:
        self.size = len(self.members)


@dataclass(frozen=True)
class MergeStep:
    """Registro de uma rodada de agrupamento UPGMA."""

    step: int
    left_id: str
    right_id: str
    new_cluster_id: str
    distance: float
    new_height: float
    left_branch_length: float
    right_branch_length: float
    left_members: tuple[str, ...]
    right_members: tuple[str, ...]
    new_members: tuple[str, ...]


@dataclass(frozen=True)
class UPGMAResult:
    """Resultado completo da construção da árvore."""

    graph: nx.DiGraph
    labels: list[str]
    distance_matrix: list[list[float]]
    merge_steps: list[MergeStep]


def build_phylogenetic_tree(sequences: list[dict[str, Any]]) -> nx.DiGraph:
    """Constrói a árvore compatível com a visualização atual do Dash."""

    return build_upgma_tree(sequences).graph


def build_example_graph(example: dict[str, Any]) -> nx.DiGraph:
    """Constrói o grafo de um exemplo e adiciona suas relações especiais.

    Hibridização e transferência horizontal continuam sendo relações manuais e
    didáticas. O UPGMA constrói apenas a árvore de bifurcações por distância; ele
    não tenta inferir biologicamente eventos reticulados.
    """

    graph = build_phylogenetic_tree(example["organisms"])

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


def build_upgma_tree(organisms: list[dict[str, Any]]) -> UPGMAResult:
    """Executa uma versão didática do UPGMA.

    Etapas usadas:

    1. Cada organismo começa como um cluster separado.
    2. A distância par a par é calculada com Needleman-Wunsch + contagem de
       mismatches/gaps. Isso evita a limitação da distância de Hamming para
       sequências de tamanhos diferentes.
    3. A cada rodada, o algoritmo agrupa os dois clusters com menor distância.
       Essa é a diferença essencial para o UPGMA: o critério não é escolher o
       maior score de alinhamento, mas sim a menor distância entre clusters.
    4. A distância do novo cluster para os demais é recalculada por média
       ponderada pelo tamanho dos clusters:

       d((A,B), C) = (|A| * d(A,C) + |B| * d(B,C)) / (|A| + |B|)

    Limitação: esta implementação é adequada para explicar o raciocínio do
    UPGMA em um jogo. Ela não substitui ferramentas científicas completas, não
    estima modelo evolutivo e não valida suposições como relógio molecular.
    """

    if len(organisms) < 2:
        raise ValueError("É necessário ter pelo menos dois organismos para montar a árvore.")

    graph = nx.DiGraph()
    active_clusters: list[Cluster] = []

    for organism in organisms:
        graph.add_node(
            organism["id"],
            label=organism["name"],
            sequence=organism["sequence"],
            description=organism.get("description", ""),
            type="organism",
            is_internal=False,
            height=0.0,
            members=[organism["id"]],
        )
        active_clusters.append(
            Cluster(
                node_id=organism["id"],
                label=organism["name"],
                members=[organism],
            )
        )

    original_labels = [organism["name"] for organism in organisms]
    original_matrix = build_distance_matrix(organisms)
    cluster_distances = _initial_cluster_distances(active_clusters)
    merge_steps: list[MergeStep] = []
    ancestor_count = 1

    while len(active_clusters) > 1:
        left_index, right_index, distance = _closest_cluster_pair(active_clusters, cluster_distances)
        left = active_clusters[left_index]
        right = active_clusters[right_index]
        ancestor_id = f"ancestor_{ancestor_count}"
        ancestor_label = f"Ancestral {ancestor_count}"
        ancestor_count += 1

        # Em UPGMA, a altura do novo nó é metade da distância entre os clusters.
        # O comprimento do ramo é a diferença entre a altura do ancestral e a
        # altura do filho. Em dados reais, valores negativos indicariam quebra da
        # suposição ultramétrica; aqui mantemos o cálculo documentado e limitamos
        # a visualização a zero para não criar ramos didáticos confusos.
        new_height = distance / 2
        left_branch = max(new_height - left.height, 0.0)
        right_branch = max(new_height - right.height, 0.0)

        merged_members = left.members + right.members
        new_cluster = Cluster(
            node_id=ancestor_id,
            label=ancestor_label,
            members=merged_members,
            height=new_height,
            children=(left, right),
        )

        graph.add_node(
            ancestor_id,
            label=ancestor_label,
            type="ancestor",
            is_internal=True,
            event_type="divergence",
            height=round(new_height, 6),
            members=[member["id"] for member in merged_members],
        )
        _add_tree_edge(graph, ancestor_id, left.node_id, left_branch, distance)
        _add_tree_edge(graph, ancestor_id, right.node_id, right_branch, distance)

        merge_steps.append(
            MergeStep(
                step=len(merge_steps) + 1,
                left_id=left.node_id,
                right_id=right.node_id,
                new_cluster_id=ancestor_id,
                distance=distance,
                new_height=new_height,
                left_branch_length=left_branch,
                right_branch_length=right_branch,
                left_members=tuple(member["name"] for member in left.members),
                right_members=tuple(member["name"] for member in right.members),
                new_members=tuple(member["name"] for member in merged_members),
            )
        )

        _update_distances_after_merge(
            distances=cluster_distances,
            active_clusters=active_clusters,
            left=left,
            right=right,
            new_cluster=new_cluster,
        )

        active_clusters = [
            cluster
            for index, cluster in enumerate(active_clusters)
            if index not in (left_index, right_index)
        ]
        active_clusters.append(new_cluster)

    graph.graph["algorithm"] = "didactic_upgma"
    graph.graph["distance_method"] = "needleman_wunsch_mismatch_gap_count"
    graph.graph["distance_matrix_labels"] = original_labels
    graph.graph["distance_matrix"] = original_matrix
    graph.graph["merge_steps"] = [step.__dict__ for step in merge_steps]

    return UPGMAResult(
        graph=graph,
        labels=original_labels,
        distance_matrix=original_matrix,
        merge_steps=merge_steps,
    )


def _add_tree_edge(
    graph: nx.DiGraph,
    source: str,
    target: str,
    branch_length: float,
    merge_distance: float,
) -> None:
    graph.add_edge(
        source,
        target,
        id=_build_edge_id(source, target),
        event_type="normal",
        is_special=False,
        label="",
        branch_length=round(branch_length, 6),
        merge_distance=round(merge_distance, 6),
    )


def _initial_cluster_distances(clusters: list[Cluster]) -> dict[frozenset[str], float]:
    distances: dict[frozenset[str], float] = {}
    for left_index in range(len(clusters) - 1):
        for right_index in range(left_index + 1, len(clusters)):
            left = clusters[left_index]
            right = clusters[right_index]
            distances[_distance_key(left.node_id, right.node_id)] = float(
                aligned_sequence_distance(left.members[0]["sequence"], right.members[0]["sequence"])
            )
    return distances


def _closest_cluster_pair(
    clusters: list[Cluster],
    distances: dict[frozenset[str], float],
) -> tuple[int, int, float]:
    """Localiza o par de clusters com menor distância atual.

    Em caso de empate, mantém o primeiro par encontrado na ordem atual dos
    clusters. Isso deixa os IDs de ancestrais previsíveis e facilita o uso no
    jogo.
    """

    best_pair = (0, 1)
    best_distance = float("inf")

    for left_index in range(len(clusters) - 1):
        for right_index in range(left_index + 1, len(clusters)):
            distance = distances[_distance_key(clusters[left_index].node_id, clusters[right_index].node_id)]
            if distance < best_distance:
                best_distance = distance
                best_pair = (left_index, right_index)

    return best_pair[0], best_pair[1], best_distance


def _update_distances_after_merge(
    distances: dict[frozenset[str], float],
    active_clusters: list[Cluster],
    left: Cluster,
    right: Cluster,
    new_cluster: Cluster,
) -> None:
    """Atualiza a matriz/dicionário de distâncias usando média ponderada."""

    for other in active_clusters:
        if other.node_id in {left.node_id, right.node_id}:
            continue
        left_distance = distances[_distance_key(left.node_id, other.node_id)]
        right_distance = distances[_distance_key(right.node_id, other.node_id)]
        weighted_distance = (
            left.size * left_distance + right.size * right_distance
        ) / (left.size + right.size)
        distances[_distance_key(new_cluster.node_id, other.node_id)] = weighted_distance

    keys_to_remove = [
        key
        for key in distances
        if left.node_id in key or right.node_id in key
    ]
    for key in keys_to_remove:
        distances.pop(key, None)


def _distance_key(left_id: str, right_id: str) -> frozenset[str]:
    return frozenset((left_id, right_id))


def _build_edge_id(source: str, target: str) -> str:
    """Cria um identificador estável para arestas no Cytoscape."""

    return f"{source}__{target}"
