"""Callbacks de interação direta com a árvore."""

from __future__ import annotations

from typing import Any

from dash import Input, Output, State, ctx, no_update

from src.free_classification import advance_relation_draft, build_custom_edge_annotation, custom_relation_exists, endpoint_id


def register_tree_interaction_callbacks(app):
    @app.callback(
        Output("selected-tree-element", "data"),
        Output("custom-relation-draft", "data", allow_duplicate=True),
        Output("user-annotations", "data", allow_duplicate=True),
        Output("free-feedback", "data", allow_duplicate=True),
        Input("phylogenetic-tree", "tapNodeData"),
        Input("phylogenetic-tree", "tapEdgeData"),
        State("game-mode", "data"),
        State("free-action-mode", "data"),
        State("custom-relation-draft", "data"),
        State("user-annotations", "data"),
        prevent_initial_call=True,
    )
    def select_tree_element(
        node_data: dict[str, Any] | None,
        edge_data: dict[str, Any] | None,
        mode: str,
        free_action_mode: str,
        draft: dict[str, Any] | None,
        annotations: list[dict[str, Any]] | None,
    ):
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update
        prop = ctx.triggered[0]["prop_id"].split(".")[-1]

        if mode == "free" and prop == "tapEdgeData" and edge_data:
            return {"id": edge_data["id"], "label": edge_data.get("label") or "Ligação evolutiva", "type": "edge", "source": edge_data["source"], "target": edge_data["target"]}, no_update, no_update, no_update

        if mode == "free" and free_action_mode == "create_relation":
            if prop == "tapNodeData" and node_data:
                next_draft = advance_relation_draft(draft, node_data)
                source = endpoint_id(next_draft.get("source"))
                target = endpoint_id(next_draft.get("target"))
                relation_type = next_draft.get("relation_type")
                if not relation_type:
                    return None, next_draft, no_update, {"type": "info", "message": "Escolha o tipo e clique em dois nós."}
                if source and target and source != target:
                    current_annotations = annotations or []
                    if custom_relation_exists(current_annotations, source, target, relation_type):
                        reset_draft = {**next_draft, "source": None, "target": None}
                        return None, reset_draft, no_update, {"type": "info", "message": "Essa relação especial já foi criada."}
                    annotation = build_custom_edge_annotation(next_draft, current_annotations)
                    reset_draft = {**next_draft, "source": None, "target": None}
                    return None, reset_draft, current_annotations + [annotation], {"type": "success", "message": f"Relação criada: {annotation['relation_label']}."}
                return None, next_draft, no_update, {"type": "info", "message": "Clique no nó de destino."}
            return no_update, no_update, no_update, no_update

        if prop == "tapNodeData" and node_data:
            return {"id": node_data["id"], "label": node_data.get("label", node_data["id"]), "type": "node"}, no_update, no_update, no_update
        if prop == "tapEdgeData" and edge_data:
            return {"id": edge_data["id"], "label": edge_data.get("label") or "Ligação evolutiva", "type": "edge", "source": edge_data["source"], "target": edge_data["target"]}, no_update, no_update, no_update
        return no_update, no_update, no_update, no_update

    @app.callback(Output("guided-reading-visible", "data"), Input("show-interpretation", "n_clicks"), State("guided-reading-visible", "data"), prevent_initial_call=True)
    def toggle_hint(_clicks: int, visible: bool) -> bool:
        return not visible

    @app.callback(Output("tree-zoom", "data"), Output("tree-pan", "data"), Output("tree-layout-seed", "data"), Input("tree-zoom-in", "n_clicks"), Input("tree-zoom-out", "n_clicks"), Input("tree-reset-view", "n_clicks"), State("tree-zoom", "data"), State("tree-pan", "data"), State("tree-layout-seed", "data"), prevent_initial_call=True)
    def tree_controls(_zoom_in: int, _zoom_out: int, _reset: int, zoom: float, pan: dict[str, int], seed: int) -> tuple[float, dict[str, int], int]:
        if ctx.triggered_id == "tree-zoom-in":
            return min(round(zoom + 0.15, 2), 2.2), pan, seed
        if ctx.triggered_id == "tree-zoom-out":
            return max(round(zoom - 0.15, 2), 0.45), pan, seed
        return 1.0, {"x": 0, "y": 0}, seed + 1
