"""Componentes do carrossel de conceitos."""

from dash import html

from frontend.state import CONCEPTS


def build_concept_card(index: int, slot: str) -> html.Article:
    title, description, icon = CONCEPTS[index]
    active = slot == "active"
    return html.Article(
        [
            html.Div(
                [
                    html.Div(icon, className="concept-icon", **{"aria-hidden": "true"}),
                    html.Span(f"{index + 1} de {len(CONCEPTS)}", className="concept-position"),
                ],
                className="concept-card-topline",
            ),
            html.H3(title),
            html.P(description),
        ],
        className="concept-carousel-card concept-card-active" if active else f"concept-carousel-card concept-card-preview {slot}",
        **{"aria-hidden": "false" if active else "true"},
    )


def build_concept_carousel(index: int) -> html.Div:
    return html.Div(
        html.Div(
            [
                build_concept_card((index - 1) % len(CONCEPTS), "left"),
                build_concept_card(index, "active"),
                build_concept_card((index + 1) % len(CONCEPTS), "right"),
            ],
            className="concept-carousel-track",
        ),
        className="concept-carousel-content",
    )

