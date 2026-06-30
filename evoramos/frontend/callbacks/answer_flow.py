"""Callbacks do fluxo de resposta dos modos com correção."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from dash import ALL, Input, Output, State, ctx, no_update

from frontend.state import EMPTY_CUSTOM_RELATION_DRAFT, EMPTY_DUEL_STATE, current_example
from src.game_rules import check_player_answer


def current_attempts(mode: str, submitted: list[dict[str, Any]], duel_state: dict[str, Any]) -> list[dict[str, Any]]:
    return duel_state.get("answers", []) if mode == "duel" else submitted


def register_answer_flow_callbacks(app):
    @app.callback(Output("selected-answer-choice", "data"), Input({"type": "answer-choice", "value": ALL}, "n_clicks"), State("selected-answer-choice", "data"), prevent_initial_call=True)
    def select_answer(_clicks: list[int], current: str | None) -> str | None:
        return ctx.triggered_id.get("value") if ctx.triggered_id else current

    @app.callback(Output({"type": "answer-choice", "value": ALL}, "className"), Input("selected-answer-choice", "data"))
    def update_answer_classes(selected: str | None) -> list[str]:
        from frontend.state import ANSWER_OPTIONS

        return ["answer-choice is-selected" if option["value"] == selected else "answer-choice" for option in ANSWER_OPTIONS]

    @app.callback(
        Output("selected-tree-element", "data", allow_duplicate=True),
        Output("selected-answer-choice", "data", allow_duplicate=True),
        Output("selected-free-classification", "data", allow_duplicate=True),
        Input("clear-selection", "n_clicks"),
        prevent_initial_call=True,
    )
    def clear_selection(_clicks: int) -> tuple[None, None, None]:
        return None, None, None

    @app.callback(
        Output("selected-tree-element", "data", allow_duplicate=True),
        Output("selected-answer-choice", "data", allow_duplicate=True),
        Output("selected-free-classification", "data"),
        Output("free-action-mode", "data"),
        Output("custom-relation-draft", "data"),
        Output("user-annotations", "data"),
        Output("free-feedback", "data"),
        Output("submitted-answers", "data"),
        Output("solo-score", "data"),
        Output("duel-state", "data"),
        Output("answer-feedback", "data"),
        Output("reveal-results", "data"),
        Output("review-highlight", "data", allow_duplicate=True),
        Output("guided-reading-visible", "data", allow_duplicate=True),
        Output("tree-zoom", "data", allow_duplicate=True),
        Output("tree-pan", "data", allow_duplicate=True),
        Input("selected-example-id", "data"),
        Input("game-mode", "data"),
        Input("reset-game", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_game(_example_id: str, _mode: str, _reset_clicks: int):
        return None, None, None, "classify", deepcopy(EMPTY_CUSTOM_RELATION_DRAFT), [], None, [], 0, deepcopy(EMPTY_DUEL_STATE), None, False, None, False, 1.0, {"x": 0, "y": 0}

    @app.callback(
        Output("submitted-answers", "data", allow_duplicate=True),
        Output("solo-score", "data", allow_duplicate=True),
        Output("duel-state", "data", allow_duplicate=True),
        Output("answer-feedback", "data", allow_duplicate=True),
        Output("selected-answer-choice", "data", allow_duplicate=True),
        Output("review-highlight", "data", allow_duplicate=True),
        Input("submit-answer", "n_clicks"),
        State("selected-example-id", "data"),
        State("game-mode", "data"),
        State("selected-tree-element", "data"),
        State("selected-answer-choice", "data"),
        State("submitted-answers", "data"),
        State("solo-score", "data"),
        State("duel-state", "data"),
        State("imported-example", "data"),
        prevent_initial_call=True,
    )
    def submit_answer(_clicks: int, example_id: str, mode: str, selected: dict[str, Any] | None, answer_type: str | None, submitted: list[dict[str, Any]], score: int, duel_state: dict[str, Any], imported_example: dict[str, Any] | None):
        if mode == "free":
            return no_update, no_update, no_update, no_update, no_update, no_update
        example = current_example(example_id, imported_example)
        player_id = duel_state["current_player"] if mode == "duel" else None
        history = duel_state.get("answers", []) if mode == "duel" else submitted
        result = check_player_answer(example, selected, answer_type, history, player_id=player_id)
        record = result.get("answer_record")

        if mode == "duel":
            next_player = 2 if duel_state["current_player"] == 1 else 1
            prefix = f"Jogador {duel_state['current_player']}"
            if record:
                result["message"] = f"{prefix} {'acertou' if result['correct'] else 'errou'}. Agora é a vez do Jogador {next_player}."
            if not record:
                return submitted, score, duel_state, result, answer_type, result.get("highlight")
            new_state = {**duel_state, "answers": duel_state.get("answers", []) + [record], "current_player": next_player}
            if result.get("points"):
                key = "player_1_score" if player_id == 1 else "player_2_score"
                new_state[key] = duel_state[key] + result["points"]
            return submitted, score, new_state, result, None, result.get("highlight")

        if not record:
            return submitted, score, duel_state, result, answer_type, result.get("highlight")
        return submitted + [record], score + result.get("points", 0), duel_state, result, None, result.get("highlight")

    @app.callback(Output("reveal-results", "data", allow_duplicate=True), Input("finish-challenge", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
    def finish_game(_clicks: int, mode: str) -> bool:
        return mode in {"solo", "duel"}

    @app.callback(Output("review-highlight", "data", allow_duplicate=True), Input({"type": "review-on-graph", "attempt": ALL}, "n_clicks"), State("submitted-answers", "data"), State("duel-state", "data"), State("game-mode", "data"), prevent_initial_call=True)
    def review_on_graph(_clicks: list[int], submitted: list[dict[str, Any]], duel_state: dict[str, Any], mode: str):
        if not ctx.triggered_id:
            return no_update
        attempt_id = ctx.triggered_id.get("attempt")
        attempts = current_attempts(mode, submitted, duel_state)
        attempt = next((item for item in attempts if item.get("attempt_id") == attempt_id), None)
        return attempt.get("highlight") if attempt else no_update

