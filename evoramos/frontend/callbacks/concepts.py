"""Callbacks do carrossel de conceitos."""

from dash import Input, Output, State, ctx

from frontend.components.concepts import build_concept_carousel
from frontend.state import CONCEPTS


def register_concept_callbacks(app):
    @app.callback(Output("concept-index", "data"), Input("previous-concept", "n_clicks"), Input("next-concept", "n_clicks"), State("concept-index", "data"), prevent_initial_call=True)
    def update_concept_index(_previous: int, _next: int, current_index: int) -> int:
        step = -1 if ctx.triggered_id == "previous-concept" else 1
        return (current_index + step) % len(CONCEPTS)

    @app.callback(Output("concept-carousel-card", "children"), Input("concept-index", "data"))
    def render_concepts(index: int):
        return build_concept_carousel(index)

