"""Callbacks do modo Classificação livre."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from dash import ALL, Input, Output, State, ctx, no_update

from frontend.state import EMPTY_CUSTOM_RELATION_DRAFT, FREE_CLASSIFICATION_OPTIONS, SPECIAL_RELATION_OPTIONS
from src.free_classification import (
    build_classification_annotation,
    remove_annotation_by_id,
    remove_classification_annotation,
    upsert_classification_annotation,
)


def register_free_classification_callbacks(app):
    @app.callback(
        Output("free-action-mode", "data", allow_duplicate=True),
        Output("selected-tree-element", "data", allow_duplicate=True),
        Output("custom-relation-draft", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("free-mode-classify", "n_clicks"),
        Input("free-mode-create-relation", "n_clicks"),
        State("custom-relation-draft", "data"),
        prevent_initial_call=True,
    )
    def choose_free_action(_classify_clicks: int, _relation_clicks: int, draft: dict[str, Any] | None):
        if ctx.triggered_id == "free-mode-create-relation":
            current = {**EMPTY_CUSTOM_RELATION_DRAFT, **(draft or {})}
            return "create_relation", None, {**current, "source": None, "target": None}, {"type": "info", "message": "Escolha o tipo, clique na origem e depois no destino."}
        return "classify", None, deepcopy(EMPTY_CUSTOM_RELATION_DRAFT), {"type": "info", "message": "Clique em um nó ou aresta para classificar."}

    @app.callback(Output("free-mode-classify", "className"), Output("free-mode-create-relation", "className"), Input("free-action-mode", "data"))
    def update_free_action_mode_classes(action_mode: str) -> tuple[str, str]:
        return (
            "classification-tab is-active" if action_mode == "classify" else "classification-tab",
            "classification-tab is-active" if action_mode == "create_relation" else "classification-tab",
        )

    @app.callback(Output("selected-free-classification", "data", allow_duplicate=True), Input({"type": "free-classification-choice", "value": ALL}, "n_clicks"), State("selected-free-classification", "data"), prevent_initial_call=True)
    def select_free_classification(_clicks: list[int], current: str | None) -> str | None:
        return ctx.triggered_id.get("value") if ctx.triggered_id else current

    @app.callback(Output({"type": "free-classification-choice", "value": ALL}, "className"), Input("selected-free-classification", "data"))
    def update_free_classification_classes(selected: str | None) -> list[str]:
        return ["answer-choice is-selected" if option["value"] == selected else "answer-choice" for option in FREE_CLASSIFICATION_OPTIONS]

    @app.callback(Output("custom-relation-draft", "data", allow_duplicate=True), Input({"type": "special-relation-choice", "value": ALL}, "n_clicks"), State("custom-relation-draft", "data"), prevent_initial_call=True)
    def select_special_relation(_clicks: list[int], draft: dict[str, Any] | None) -> dict[str, Any]:
        if not ctx.triggered_id:
            return no_update
        current = {**EMPTY_CUSTOM_RELATION_DRAFT, **(draft or {})}
        return {**current, "relation_type": ctx.triggered_id.get("value")}

    @app.callback(Output({"type": "special-relation-choice", "value": ALL}, "className"), Input("custom-relation-draft", "data"))
    def update_special_relation_classes(draft: dict[str, Any] | None) -> list[str]:
        selected = (draft or {}).get("relation_type")
        return ["answer-choice is-selected" if option["value"] == selected else "answer-choice" for option in SPECIAL_RELATION_OPTIONS]

    @app.callback(
        Output("user-annotations", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("apply-classification", "n_clicks"),
        State("game-mode", "data"),
        State("selected-tree-element", "data"),
        State("selected-free-classification", "data"),
        State("user-annotations", "data"),
        prevent_initial_call=True,
    )
    def apply_free_classification(_clicks: int, mode: str, selected: dict[str, Any] | None, relation_type: str | None, annotations: list[dict[str, Any]] | None):
        if mode != "free":
            return no_update, no_update
        if not selected:
            return no_update, {"type": "error", "message": "Clique em um nó ou aresta antes de aplicar."}
        if not relation_type:
            return no_update, {"type": "error", "message": "Escolha uma classificação."}
        annotation = build_classification_annotation(selected, relation_type)
        updated = upsert_classification_annotation(annotations or [], annotation)
        return updated, {"type": "success", "message": f"Classificação aplicada: {annotation['relation_label']}."}

    @app.callback(
        Output("user-annotations", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("remove-classification", "n_clicks"),
        State("game-mode", "data"),
        State("selected-tree-element", "data"),
        State("user-annotations", "data"),
        prevent_initial_call=True,
    )
    def remove_free_classification(_clicks: int, mode: str, selected: dict[str, Any] | None, annotations: list[dict[str, Any]] | None):
        if mode != "free":
            return no_update, no_update
        if not selected:
            return no_update, {"type": "error", "message": "Selecione o elemento primeiro."}
        current_annotations = annotations or []
        updated = remove_classification_annotation(current_annotations, selected)
        if len(updated) == len(current_annotations):
            return no_update, {"type": "info", "message": "Este elemento não tinha classificação."}
        return updated, {"type": "success", "message": "Classificação removida."}

    @app.callback(
        Output("custom-relation-draft", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("cancel-relation", "n_clicks"),
        State("custom-relation-draft", "data"),
        prevent_initial_call=True,
    )
    def cancel_custom_relation(_clicks: int, draft: dict[str, Any] | None):
        current = {**EMPTY_CUSTOM_RELATION_DRAFT, **(draft or {})}
        return {**current, "source": None, "target": None}, {"type": "info", "message": "Criação cancelada."}

    @app.callback(
        Output("user-annotations", "data", allow_duplicate=True),
        Output("custom-relation-draft", "data", allow_duplicate=True),
        Output("selected-tree-element", "data", allow_duplicate=True),
        Output("selected-free-classification", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("clear-free-annotations", "n_clicks"),
        State("game-mode", "data"),
        prevent_initial_call=True,
    )
    def clear_free_annotations(_clicks: int, mode: str):
        if mode != "free":
            return no_update, no_update, no_update, no_update, no_update
        return [], deepcopy(EMPTY_CUSTOM_RELATION_DRAFT), None, None, {"type": "success", "message": "Anotações livres removidas."}

    @app.callback(
        Output("user-annotations", "data", allow_duplicate=True),
        Output("selected-tree-element", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("delete-selected-relation", "n_clicks"),
        State("game-mode", "data"),
        State("selected-tree-element", "data"),
        State("user-annotations", "data"),
        prevent_initial_call=True,
    )
    def delete_selected_relation(_clicks: int, mode: str, selected: dict[str, Any] | None, annotations: list[dict[str, Any]] | None):
        if mode != "free" or not selected or selected.get("type") != "edge":
            return no_update, no_update, no_update
        edge_id = selected.get("id")
        current_annotations = annotations or []
        is_custom_edge = any(item.get("kind") == "custom_edge" and item.get("edge_id") == edge_id for item in current_annotations)
        if not is_custom_edge:
            return no_update, no_update, {"type": "info", "message": "Selecione uma relação especial criada por você."}
        return remove_annotation_by_id(current_annotations, edge_id), None, {"type": "success", "message": "Relação especial excluída."}

    @app.callback(
        Output("user-annotations", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input({"type": "remove-user-annotation", "id": ALL}, "n_clicks"),
        State("user-annotations", "data"),
        prevent_initial_call=True,
    )
    def remove_user_annotation(_clicks: list[int], annotations: list[dict[str, Any]] | None):
        if not ctx.triggered_id:
            return no_update, no_update
        remove_id = ctx.triggered_id.get("id")
        return remove_annotation_by_id(annotations or [], remove_id), {"type": "success", "message": "Anotação removida."}

    @app.callback(Output("phylogenetic-tree", "generateImage"), Input("download-annotated-tree", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
    def download_annotated_tree(_clicks: int, mode: str):
        filename = "arvore_anotada" if mode == "free" else "arvore_evoramos"
        return {"type": "png", "action": "download", "filename": filename}
