"""Callbacks de seleção dos exemplos/exercícios."""

from dash import ALL, Input, Output, State, ctx

from frontend.components.exercises import build_exercise_cards
from frontend.state import EXAMPLES, available_examples


def register_exercise_selection_callbacks(app):
    @app.callback(Output("exercise-card-grid", "children"), Input("selected-example-id", "data"), Input("imported-example", "data"))
    def render_exercise_grid(selected_id: str, imported_example: dict | None):
        return build_exercise_cards(selected_id, imported_example)

    @app.callback(Output("selected-example-id", "data"), Input({"type": "exercise-card", "index": ALL}, "n_clicks"), State("selected-example-id", "data"), prevent_initial_call=True)
    def select_example(_clicks: list[int], current: str) -> str:
        return ctx.triggered_id.get("index") if ctx.triggered_id else current

    @app.callback(Output({"type": "exercise-card", "index": ALL}, "className"), Input("selected-example-id", "data"), Input("imported-example", "data"))
    def update_exercise_classes(selected_id: str, imported_example: dict | None) -> list[str]:
        return ["exercise-card is-active" if example["id"] == selected_id else "exercise-card" for example in available_examples(imported_example)]

