"""Componentes de seleção de modo e exercícios."""

from __future__ import annotations

from typing import Any

from dash import html

from frontend.state import GAME_MODES, IMPORTED_EXAMPLE_ID, available_examples


def build_mode_selector(active_mode: str) -> html.Div:
    return html.Div(
        [
            html.Button(label, id=f"mode-{mode_id}", n_clicks=0, className="mode-card is-active" if mode_id == active_mode else "mode-card")
            for mode_id, label in GAME_MODES.items()
        ],
        className="mode-selector",
    )


def build_exercise_cards(selected_id: str, imported_example: dict[str, Any] | None = None) -> list[html.Button]:
    cards: list[html.Button] = []
    for index, example in enumerate(available_examples(imported_example), start=1):
        active = example["id"] == selected_id
        eyebrow = "Sequências importadas" if example["id"] == IMPORTED_EXAMPLE_ID else f"Exercício {index}"
        cards.append(
            html.Button(
                [
                    html.Div(
                        [
                            html.Span(eyebrow, className="eyebrow"),
                            html.Span(example["difficulty"], className=f"difficulty-badge difficulty-{example['difficulty'].lower()}"),
                        ],
                        className="card-topline",
                    ),
                    html.H3(example["title"]),
                    html.P(example["description"]),
                ],
                id={"type": "exercise-card", "index": example["id"]},
                n_clicks=0,
                className="exercise-card is-active" if active else "exercise-card",
            )
        )
    return cards

