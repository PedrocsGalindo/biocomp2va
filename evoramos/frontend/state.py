"""Constantes e estado inicial compartilhados pela interface Dash."""

from __future__ import annotations

from typing import Any

from src.example_loader import get_example_by_id, load_examples

CONCEPTS = [
    ("DNA", "O DNA armazena a informação genética dos organismos. Aqui, ele é representado pelas letras A, T, C e G.", "DNA"),
    ("Sequência genética", "É a ordem das bases do DNA. Quanto mais parecidas duas sequências, maior pode ser a proximidade evolutiva.", "SEQ"),
    ("Mutação", "É uma alteração na sequência genética. Pequenas mudanças acumuladas ajudam a diferenciar espécies ao longo do tempo.", "MUT"),
    ("Árvore filogenética", "Representa relações evolutivas, proximidades, ancestrais comuns e separações entre linhagens.", "TREE"),
    ("Especiação", "É o surgimento de novas espécies a partir de uma linhagem ancestral, geralmente mostrado por uma bifurcação.", "SP"),
    ("Hibridização", "Ocorre quando uma linhagem recebe contribuição genética de duas linhagens diferentes.", "HYB"),
    ("Transferência horizontal", "Material genético passa entre organismos sem relação direta de ancestralidade.", "HGT"),
]

GAME_MODES = {
    "learning": "Aprendizado",
    "solo": "Desafio individual",
    "duel": "Duelo local",
    "free": "Classificação livre",
}

ANSWER_OPTIONS = [
    {"label": "Especiação", "value": "speciation"},
    {"label": "Hibridização", "value": "hybridization"},
    {"label": "Transferência horizontal", "value": "horizontal_transfer"},
    {"label": "Não é evento especial", "value": "none"},
]

FREE_CLASSIFICATION_OPTIONS = [
    {"label": "Especiação", "value": "speciation"},
    {"label": "Relação ancestral comum", "value": "common_ancestor"},
    {"label": "Não classificado", "value": "unclassified"},
]

SPECIAL_RELATION_OPTIONS = [
    {"label": "Transferência horizontal", "value": "horizontal_transfer"},
    {"label": "Hibridização / contribuição genética", "value": "hybridization"},
]

IMPORTED_EXAMPLE_ID = "imported_sequences"
EMPTY_CUSTOM_RELATION_DRAFT = {"source": None, "target": None, "relation_type": None}

EMPTY_DUEL_STATE = {
    "current_player": 1,
    "player_1_score": 0,
    "player_2_score": 0,
    "answers": [],
}

DEFAULT_TREE_LAYOUT = {
    "name": "breadthfirst",
    "directed": True,
    "spacingFactor": 1.55,
    "padding": 38,
    "animate": True,
    "fit": True,
}

EXAMPLES = load_examples()
FIRST_EXAMPLE = EXAMPLES[0]


def available_examples(imported_example: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    examples = list(EXAMPLES)
    if imported_example:
        examples.append(imported_example)
    return examples


def current_example(example_id: str, imported_example: dict[str, Any] | None = None) -> dict[str, Any]:
    if imported_example and example_id == imported_example.get("id"):
        return imported_example
    if example_id == IMPORTED_EXAMPLE_ID:
        return FIRST_EXAMPLE
    return get_example_by_id(EXAMPLES, example_id)
