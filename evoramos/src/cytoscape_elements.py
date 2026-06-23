"""Conversão de grafos NetworkX para elementos do Dash Cytoscape."""

import networkx as nx


def build_cytoscape_elements(graph: nx.Graph) -> list[dict]:
    """Converte os nós e as arestas de um grafo para o formato Cytoscape."""
    elements = []

    for node_id, attributes in graph.nodes(data=True):
        elements.append(
            {
                "data": {
                    "id": str(node_id),
                    "label": attributes.get("label", str(node_id)),
                    **attributes,
                }
            }
        )

    for source, target, attributes in graph.edges(data=True):
        elements.append(
            {
                "data": {
                    "source": str(source),
                    "target": str(target),
                    "label": str(attributes.get("distance", "")),
                    **attributes,
                }
            }
        )

    return elements
