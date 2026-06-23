"""Construção inicial da árvore filogenética do EvoRamos."""

from typing import Any

import networkx as nx

from src.distance import hamming_distance


def build_phylogenetic_tree(sequences: list[dict[str, Any]]) -> nx.Graph:
    """Cria um grafo simples de exemplo a partir dos organismos.

    Este placeholder conecta os organismos em sequência e registra a distância
    de Hamming entre cada par vizinho. Um algoritmo filogenético real será
    incluído em uma etapa futura do projeto.
    """
    graph = nx.Graph()

    for organism in sequences:
        graph.add_node(
            organism["id"],
            label=organism["name"],
            sequence=organism["sequence"],
        )

    for current, following in zip(sequences, sequences[1:]):
        graph.add_edge(
            current["id"],
            following["id"],
            distance=hamming_distance(
                current["sequence"],
                following["sequence"],
            ),
        )

    return graph
