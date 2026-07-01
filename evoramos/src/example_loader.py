"""Carregamento, validação e consulta dos exercícios do EvoRamos."""

import json
from pathlib import Path
from typing import Any


DEFAULT_EXAMPLES_FILE = Path(__file__).resolve().parents[1] / "data" / "examples.json"
REQUIRED_EXAMPLE_FIELDS = {
    "id",
    "title",
    "difficulty",
    "description",
    "learning_goal",
    "organisms",
    "expected_events",
    "explanation",
    "optional_edges",
    "tree_mode",
}
REQUIRED_ORGANISM_FIELDS = {"id", "name", "sequence", "description"}
REQUIRED_OPTIONAL_EDGE_FIELDS = {"source", "target", "event_type"}
REQUIRED_EXPECTED_EVENT_FIELDS = {
    "id",
    "target_id",
    "target_type",
    "event_type",
    "label",
    "explanation",
}
VALID_EVENT_TYPES = {"speciation", "hybridization", "horizontal_transfer"}
VALID_TARGET_TYPES = {"node", "edge"}


def load_examples(file_path: Path = DEFAULT_EXAMPLES_FILE) -> list[dict[str, Any]]:
    """Carrega os exemplos e valida o esquema necessário pelo app."""
    with file_path.open(encoding="utf-8") as file:
        examples = json.load(file)

    if not isinstance(examples, list) or not examples:
        raise ValueError("O arquivo de exemplos deve conter uma lista não vazia.")

    example_ids: set[str] = set()
    for index, example in enumerate(examples, start=1):
        _validate_example(example, index)
        if example["id"] in example_ids:
            raise ValueError(f"ID de exemplo duplicado: {example['id']}")
        example_ids.add(example["id"])

    return examples


def get_example_by_id(
    examples: list[dict[str, Any]], example_id: str | None
) -> dict[str, Any]:
    """Retorna o exemplo solicitado ou usa o primeiro como fallback seguro."""
    if not examples:
        raise ValueError("Nenhum exemplo está disponível.")

    for example in examples:
        if example.get("id") == example_id:
            return example

    return examples[0]


def _validate_example(example: Any, index: int) -> None:
    """Valida campos principais, organismos, eventos esperados e arestas especiais."""
    if not isinstance(example, dict):
        raise ValueError(f"O exemplo na posição {index} deve ser um objeto.")

    missing = REQUIRED_EXAMPLE_FIELDS - example.keys()
    if missing:
        raise ValueError(
            f"Exemplo {example.get('id', index)} sem campos: {sorted(missing)}"
        )

    for field in (
        "id",
        "title",
        "difficulty",
        "description",
        "learning_goal",
        "explanation",
        "tree_mode",
    ):
        if not isinstance(example[field], str) or not example[field].strip():
            raise ValueError(
                f"Campo '{field}' inválido no exemplo {example.get('id', index)}."
            )

    organisms = example["organisms"]
    if not isinstance(organisms, list) or not organisms:
        raise ValueError(f"O exemplo {example['id']} precisa ter organismos.")

    organism_ids: set[str] = set()
    for organism in organisms:
        if not isinstance(organism, dict):
            raise ValueError(f"Organismo inválido no exemplo {example['id']}.")
        missing_organism_fields = REQUIRED_ORGANISM_FIELDS - organism.keys()
        if missing_organism_fields:
            raise ValueError(
                f"Organismo do exemplo {example['id']} sem campos: "
                f"{sorted(missing_organism_fields)}"
            )
        if organism["id"] in organism_ids:
            raise ValueError(
                f"ID de organismo duplicado no exemplo {example['id']}: "
                f"{organism['id']}"
            )
        organism_ids.add(organism["id"])

        for field in REQUIRED_ORGANISM_FIELDS:
            if not isinstance(organism[field], str) or not organism[field].strip():
                raise ValueError(
                    f"Campo '{field}' inválido em organismo do exemplo "
                    f"{example['id']}."
                )

        sequence = organism["sequence"]
        if set(sequence.upper()) - {"A", "T", "C", "G", "N"}:
            raise ValueError(f"Sequência inválida no exemplo {example['id']}.")

    if not isinstance(example["expected_events"], list):
        raise ValueError(f"expected_events inválido no exemplo {example['id']}.")

    expected_event_ids: set[str] = set()
    for event in example["expected_events"]:
        if not isinstance(event, dict):
            raise ValueError(
                f"Evento esperado inválido no exemplo {example['id']}."
            )
        missing_event_fields = REQUIRED_EXPECTED_EVENT_FIELDS - event.keys()
        if missing_event_fields:
            raise ValueError(
                f"Evento esperado do exemplo {example['id']} sem campos: "
                f"{sorted(missing_event_fields)}"
            )
        if event["id"] in expected_event_ids:
            raise ValueError(
                f"Evento esperado duplicado no exemplo {example['id']}: {event['id']}"
            )
        expected_event_ids.add(event["id"])
        if event["event_type"] not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Tipo de evento inválido no exemplo {example['id']}: "
                f"{event['event_type']}"
            )
        if event["target_type"] not in VALID_TARGET_TYPES:
            raise ValueError(
                f"Tipo de alvo inválido no exemplo {example['id']}: "
                f"{event['target_type']}"
            )
        for field in REQUIRED_EXPECTED_EVENT_FIELDS:
            if not isinstance(event[field], str) or not event[field].strip():
                raise ValueError(
                    f"Campo '{field}' inválido em evento do exemplo {example['id']}."
                )

    if not isinstance(example["optional_edges"], list):
        raise ValueError(f"optional_edges inválido no exemplo {example['id']}.")

    valid_edge_targets = organism_ids | {
        event["target_id"]
        for event in example["expected_events"]
        if event["target_type"] == "node"
    }
    for edge in example["optional_edges"]:
        if not isinstance(edge, dict):
            raise ValueError(f"Aresta especial inválida no exemplo {example['id']}.")
        missing_edge_fields = REQUIRED_OPTIONAL_EDGE_FIELDS - edge.keys()
        if missing_edge_fields:
            raise ValueError(
                f"Aresta do exemplo {example['id']} sem campos: "
                f"{sorted(missing_edge_fields)}"
            )
        if edge["source"] not in organism_ids:
            raise ValueError(
                f"Aresta do exemplo {example['id']} referencia origem inexistente."
            )
        if edge["target"] not in valid_edge_targets:
            raise ValueError(
                f"Aresta do exemplo {example['id']} referencia destino inexistente."
            )
        if edge["event_type"] not in VALID_EVENT_TYPES:
            raise ValueError(
                f"Tipo de aresta inválido no exemplo {example['id']}."
            )
