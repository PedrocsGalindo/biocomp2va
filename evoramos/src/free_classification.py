"""Lógica pura da classificação livre e das relações especiais."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

CLASSIFICATION_LABELS = {
    "speciation": "Especiação",
    "common_ancestor": "Relação ancestral comum",
    "unclassified": "Não classificado",
    "hybridization": "Hibridização",
    "horizontal_transfer": "Transferência horizontal",
}

SPECIAL_RELATION_LABELS = {
    "horizontal_transfer": "Transferência horizontal",
    "hybridization": "Contribuição híbrida",
}

EMPTY_CUSTOM_RELATION_DRAFT = {"source": None, "target": None, "relation_type": None}


def classification_label(relation_type: str | None) -> str:
    if not relation_type:
        return "Nenhuma classificação escolhida"
    return CLASSIFICATION_LABELS.get(relation_type, relation_type)


def special_relation_label(relation_type: str | None) -> str:
    return SPECIAL_RELATION_LABELS.get(relation_type or "", "Tipo não escolhido")


def annotation_identifier(annotation: dict[str, Any]) -> str:
    return annotation.get("annotation_id") or annotation.get("edge_id") or annotation.get("element_id", "")


def annotation_kind_label(annotation: dict[str, Any]) -> str:
    return "Relação criada" if annotation.get("kind") == "custom_edge" else "Classificação"


def annotation_title(annotation: dict[str, Any]) -> str:
    if annotation.get("kind") == "custom_edge":
        return f"{annotation.get('relation_label', 'Relação')}: {annotation.get('source_label', annotation.get('source'))} → {annotation.get('target_label', annotation.get('target'))}"
    return f"{annotation.get('relation_label', 'Classificação')}: {annotation.get('element_label', annotation.get('element_id'))}"


def annotation_detail(annotation: dict[str, Any]) -> str:
    if annotation.get("kind") == "custom_edge":
        return "Aresta especial criada manualmente entre dois nós da árvore."
    element_type = "nó" if annotation.get("element_type") == "node" else "aresta"
    return f"Classificação aplicada a um {element_type} existente."


def selected_element_label_for_record(selected: dict[str, Any]) -> str:
    if selected.get("type") == "edge":
        return selected.get("label") or f"{selected.get('source')} → {selected.get('target')}"
    return selected.get("label") or selected.get("id", "Elemento selecionado")


def build_classification_annotation(selected: dict[str, Any], relation_type: str) -> dict[str, Any]:
    element_id = selected.get("id")
    element_type = selected.get("type")
    annotation = {
        "kind": "annotation",
        "annotation_id": f"annotation_{element_type}_{element_id}",
        "element_id": element_id,
        "element_type": element_type,
        "element_label": selected_element_label_for_record(selected),
        "relation_type": relation_type,
        "relation_label": classification_label(relation_type),
    }
    if selected.get("type") == "edge":
        annotation["source"] = selected.get("source")
        annotation["target"] = selected.get("target")
    return annotation


def upsert_classification_annotation(annotations: list[dict[str, Any]], annotation: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in annotations
        if not (
            item.get("kind") == "annotation"
            and item.get("element_id") == annotation.get("element_id")
            and item.get("element_type") == annotation.get("element_type")
        )
    ] + [annotation]


def remove_classification_annotation(annotations: list[dict[str, Any]], selected: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not selected:
        return annotations
    return [
        item
        for item in annotations
        if not (
            item.get("kind") == "annotation"
            and item.get("element_id") == selected.get("id")
            and item.get("element_type") == selected.get("type")
        )
    ]


def remove_annotation_by_id(annotations: list[dict[str, Any]], remove_id: str) -> list[dict[str, Any]]:
    return [item for item in annotations if annotation_identifier(item) != remove_id]


def next_custom_edge_id(annotations: list[dict[str, Any]]) -> str:
    used = {item.get("edge_id") for item in annotations if item.get("kind") == "custom_edge"}
    index = 1
    while True:
        edge_id = f"custom_edge_{index:02d}"
        if edge_id not in used:
            return edge_id
        index += 1


def build_custom_edge_annotation(draft: dict[str, Any], annotations: list[dict[str, Any]]) -> dict[str, Any]:
    source = draft.get("source")
    target = draft.get("target")
    relation_type = draft.get("relation_type")
    return {
        "kind": "custom_edge",
        "edge_id": next_custom_edge_id(annotations),
        "source": endpoint_id(source),
        "target": endpoint_id(target),
        "source_label": relation_endpoint_text(source),
        "target_label": relation_endpoint_text(target),
        "relation_type": relation_type,
        "relation_label": special_relation_label(relation_type),
    }


def custom_relation_exists(annotations: list[dict[str, Any]], source: str, target: str, relation_type: str) -> bool:
    return any(
        item.get("kind") == "custom_edge"
        and item.get("source") == source
        and item.get("target") == target
        and item.get("relation_type") == relation_type
        for item in annotations
    )


def endpoint_id(endpoint: Any) -> str | None:
    if isinstance(endpoint, dict):
        return endpoint.get("id")
    return endpoint


def endpoint_from_node(node_data: dict[str, Any]) -> dict[str, str]:
    return {"id": node_data["id"], "label": node_data.get("label", node_data["id"])}


def relation_endpoint_text(endpoint: dict[str, Any] | None) -> str:
    if not endpoint:
        return "Nenhum nó selecionado"
    return endpoint.get("label") or endpoint.get("id", "Nó selecionado")


def advance_relation_draft(draft: dict[str, Any] | None, node_data: dict[str, Any]) -> dict[str, Any]:
    current = {**EMPTY_CUSTOM_RELATION_DRAFT, **(draft or {})}
    endpoint = endpoint_from_node(node_data)
    source_id = endpoint_id(current.get("source"))
    target_id = endpoint_id(current.get("target"))

    if not source_id or target_id:
        return {**current, "source": endpoint, "target": None}
    if endpoint["id"] == source_id:
        return current
    return {**current, "target": endpoint}


def apply_user_annotations(elements: list[dict[str, Any]], annotations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated_elements = deepcopy(elements)
    node_labels = {element["data"]["id"]: element["data"].get("label", element["data"]["id"]) for element in annotated_elements if "source" not in element["data"]}
    node_ids = set(node_labels)

    for annotation in annotations:
        relation_type = annotation.get("relation_type")
        relation_label = annotation.get("relation_label") or classification_label(relation_type)
        if annotation.get("kind") == "annotation":
            element = find_cytoscape_element(annotated_elements, annotation.get("element_id"), annotation.get("element_type"))
            if not element:
                continue
            element["data"]["relation_type"] = relation_type
            element["data"]["relation_label"] = relation_label
            element["data"]["label"] = element["data"].get("label", annotation.get("element_label", ""))
            element["classes"] = append_classes(element.get("classes", ""), ["user-annotated-node" if annotation.get("element_type") == "node" else "user-annotated-edge", user_relation_class(relation_type)])
            if annotation.get("element_type") == "node":
                base_label = element["data"].get("label") or annotation.get("element_label") or annotation.get("element_id")
                element["data"]["display_label"] = f"{base_label}\n{relation_label}"
            else:
                element["data"]["label"] = relation_label
        elif annotation.get("kind") == "custom_edge":
            source = annotation.get("source")
            target = annotation.get("target")
            if not source or not target or source == target or source not in node_ids or target not in node_ids:
                continue
            annotated_elements.append(
                {
                    "data": {
                        "id": annotation.get("edge_id"),
                        "source": source,
                        "target": target,
                        "relation_type": relation_type,
                        "relation_label": relation_label,
                        "label": relation_label,
                    },
                    "classes": append_classes("user-custom-edge user-annotated-edge", [user_relation_class(relation_type)]),
                }
            )
    return annotated_elements


def find_cytoscape_element(elements: list[dict[str, Any]], element_id: str | None, element_type: str | None) -> dict[str, Any] | None:
    if not element_id or not element_type:
        return None
    for element in elements:
        data = element.get("data", {})
        is_edge = "source" in data
        if data.get("id") == element_id and ((element_type == "edge") == is_edge):
            return element
    return None


def append_classes(current: str, classes: list[str]) -> str:
    merged = current.split()
    for class_name in classes:
        if class_name and class_name not in merged:
            merged.append(class_name)
    return " ".join(merged)


def user_relation_class(relation_type: str | None) -> str:
    if not relation_type:
        return ""
    return f"user-{relation_type.replace('_', '-')}"

