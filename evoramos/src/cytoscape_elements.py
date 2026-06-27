"""Conversão de grafos NetworkX para elementos do Dash Cytoscape."""

import networkx as nx


def build_cytoscape_elements(graph: nx.Graph) -> list[dict]:
    """Converte os nós e as arestas de um grafo para o formato Cytoscape."""
    elements = []

    for node_id, attributes in graph.nodes(data=True):
        node_data = {
            "id": str(node_id),
            "label": attributes.get("label", str(node_id)),
            **attributes,
        }
        elements.append(
            {
                "data": node_data,
                "classes": _node_classes(attributes),
            }
        )

    for source, target, attributes in graph.edges(data=True):
        edge_data = {
            "id": str(attributes.get("id", f"{source}__{target}")),
            "source": str(source),
            "target": str(target),
            "label": str(attributes.get("label", "")),
            **attributes,
        }
        elements.append(
            {
                "data": edge_data,
                "classes": _edge_classes(attributes),
            }
        )

    return elements


def _node_classes(attributes: dict) -> str:
    """Gera classes visuais a partir dos atributos do nó."""
    classes = ["internal-node" if attributes.get("is_internal") else "organism-node"]
    if attributes.get("event_type") == "speciation":
        classes.append("speciation-node")
    if attributes.get("event_type") == "hybridization":
        classes.append("hybrid-node")
    return " ".join(classes)


def _edge_classes(attributes: dict) -> str:
    """Gera classes visuais a partir do tipo da aresta."""
    event_type = attributes.get("event_type", "normal")
    return {
        "hybridization": "hybrid-edge",
        "horizontal_transfer": "transfer-edge",
    }.get(event_type, "normal-edge")
