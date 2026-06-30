"""Callback principal que renderiza a tela a partir dos stores."""

from __future__ import annotations

from typing import Any

from dash import Input, Output, html

from frontend.components.correction_review import build_correction_section, build_results_summary
from frontend.components.free_classification_panel import build_free_feedback, build_relation_progress, free_selected_element_text
from frontend.components.game_sidebar import build_sidebar_heading, build_status_bar, selected_element_text, sidebar_message
from frontend.components.tree_view import build_guided_hint, build_instructions_strip, build_legend, build_organism_table, tree_payload
from frontend.state import DEFAULT_TREE_LAYOUT, EMPTY_CUSTOM_RELATION_DRAFT, current_example
from src.free_classification import relation_endpoint_text, special_relation_label


def register_render_callbacks(app):
    @app.callback(
        Output("game-status-bar", "children"),
        Output("game-status-bar", "style"),
        Output("game-instructions-shell", "children"),
        Output("main-game-layout", "className"),
        Output("tree-column", "className"),
        Output("game-sidebar", "className"),
        Output("sidebar-heading", "children"),
        Output("answer-panel", "className"),
        Output("free-panel", "className"),
        Output("free-classify-panel", "className"),
        Output("free-relation-panel", "className"),
        Output("download-annotated-tree", "className"),
        Output("clear-free-annotations", "className"),
        Output("delete-selected-relation", "className"),
        Output("selected-element-label", "children"),
        Output("selected-element-type", "children"),
        Output("finish-challenge", "children"),
        Output("reset-game", "children"),
        Output("answer-feedback-box", "children"),
        Output("answer-feedback-box", "className"),
        Output("free-selected-element-label", "children"),
        Output("free-selected-element-type", "children"),
        Output("free-draft-source", "children"),
        Output("free-draft-target", "children"),
        Output("free-draft-type", "children"),
        Output("free-relation-progress", "children"),
        Output("free-feedback-box", "children"),
        Output("free-feedback-box", "className"),
        Output("results-summary", "children"),
        Output("legend-wrapper", "children"),
        Output("interpretation-panel", "children"),
        Output("learning-goal", "children"),
        Output("secondary-goal-copy", "children"),
        Output("secondary-description", "children"),
        Output("secondary-explanation", "children"),
        Output("organism-table", "children"),
        Output("secondary-content", "className"),
        Output("phylogenetic-tree", "elements"),
        Output("phylogenetic-tree", "stylesheet"),
        Output("phylogenetic-tree", "zoom"),
        Output("phylogenetic-tree", "pan"),
        Output("phylogenetic-tree", "layout"),
        Input("selected-example-id", "data"),
        Input("imported-example", "data"),
        Input("game-mode", "data"),
        Input("selected-tree-element", "data"),
        Input("selected-answer-choice", "data"),
        Input("selected-free-classification", "data"),
        Input("free-action-mode", "data"),
        Input("custom-relation-draft", "data"),
        Input("user-annotations", "data"),
        Input("free-feedback", "data"),
        Input("submitted-answers", "data"),
        Input("solo-score", "data"),
        Input("duel-state", "data"),
        Input("answer-feedback", "data"),
        Input("reveal-results", "data"),
        Input("review-highlight", "data"),
        Input("guided-reading-visible", "data"),
        Input("tree-zoom", "data"),
        Input("tree-pan", "data"),
        Input("tree-layout-seed", "data"),
    )
    def render_app_state(
        example_id: str,
        imported_example: dict[str, Any] | None,
        mode: str,
        selected: dict[str, Any] | None,
        answer_choice: str | None,
        selected_free_classification: str | None,
        free_action_mode: str,
        custom_relation_draft: dict[str, Any] | None,
        user_annotations: list[dict[str, Any]],
        free_feedback: dict[str, Any] | None,
        submitted: list[dict[str, Any]],
        score: int,
        duel_state: dict[str, Any],
        feedback: dict[str, Any] | None,
        reveal: bool,
        highlight: dict[str, list[str]] | None,
        hint_visible: bool,
        zoom: float,
        pan: dict[str, int],
        layout_seed: int,
    ):
        del answer_choice

        example = current_example(example_id, imported_example)
        free_annotations = user_annotations or []
        draft = {**EMPTY_CUSTOM_RELATION_DRAFT, **(custom_relation_draft or {})}
        active_highlight = None if mode == "free" else highlight
        elements, stylesheet = tree_payload(example, mode, reveal, selected, active_highlight, free_annotations, draft)
        status_children, status_style = build_status_bar(mode, example, score, submitted, duel_state)
        selected_label, selected_type = selected_element_text(selected)
        free_selected_label, free_selected_type = free_selected_element_text(selected, selected_free_classification)
        free_feedback_text, free_feedback_class = build_free_feedback(free_feedback)
        sidebar_feedback = sidebar_message(feedback)
        feedback_class = "feedback-box"
        if feedback:
            feedback_class += " correct" if feedback.get("correct") else " incorrect"

        if mode == "learning":
            layout_class = "game-layout learning-layout"
            tree_class = "game-tree-column is-learning learning-full-width"
            sidebar_class = "game-sidebar is-hidden"
        elif mode == "free":
            layout_class = "game-layout free-layout"
            tree_class = "game-tree-column is-game-mode is-free-mode"
            sidebar_class = "game-sidebar is-hidden"
        else:
            layout_class = "game-layout inline-play-layout"
            tree_class = "game-tree-column is-game-mode is-play-mode"
            sidebar_class = "game-sidebar is-hidden"
        answer_panel_class = "answer-panel inline-answer-panel" if mode in {"solo", "duel"} else "answer-panel inline-answer-panel is-hidden"
        free_panel_class = "classification-panel compact-free-panel" if mode == "free" else "classification-panel compact-free-panel is-hidden"
        free_classify_panel_class = "classification-section compact-classify-flow" if free_action_mode == "classify" else "classification-section compact-classify-flow is-hidden"
        free_relation_panel_class = "classification-section special-relation-flow compact-relation-flow" if free_action_mode == "create_relation" else "classification-section special-relation-flow compact-relation-flow is-hidden"
        download_action_class = "tree-small-action download-tree-button"
        clear_action_class = "tree-small-action clear-tree-button" if mode == "free" else "tree-small-action clear-tree-button is-hidden"
        selected_custom_edge = (
            mode == "free"
            and selected
            and selected.get("type") == "edge"
            and any(item.get("kind") == "custom_edge" and item.get("edge_id") == selected.get("id") for item in free_annotations)
        )
        delete_relation_class = "tree-small-action danger-icon-button" if selected_custom_edge else "tree-small-action danger-icon-button is-hidden"
        secondary_class = "secondary-content-stack is-hidden"
        finish_label = "Encerrar duelo" if mode == "duel" else "Finalizar desafio"
        reset_label = "Reiniciar duelo" if mode == "duel" else "Reiniciar desafio"
        summary = build_results_summary(mode, example, score, submitted, duel_state) if mode not in {"learning", "free"} and reveal else None
        correction = "" if mode == "free" else build_correction_section(feedback, mode, reveal, summary)
        explanation_text = example["explanation"] if mode in {"learning", "free"} or reveal else "Finalize o modo atual para revelar a explicação completa."
        layout = {**DEFAULT_TREE_LAYOUT, "padding": 38 + (layout_seed % 2)}

        return (
            status_children,
            status_style,
            build_instructions_strip(mode, hint_visible),
            layout_class,
            tree_class,
            sidebar_class,
            build_sidebar_heading(mode),
            answer_panel_class,
            free_panel_class,
            free_classify_panel_class,
            free_relation_panel_class,
            download_action_class,
            clear_action_class,
            delete_relation_class,
            selected_label,
            selected_type,
            finish_label,
            reset_label,
            sidebar_feedback,
            feedback_class,
            free_selected_label,
            free_selected_type,
            relation_endpoint_text(draft.get("source")),
            relation_endpoint_text(draft.get("target")),
            special_relation_label(draft.get("relation_type")),
            build_relation_progress(draft),
            free_feedback_text,
            free_feedback_class,
            correction,
            build_legend(mode if not reveal else "learning"),
            build_guided_hint(example, mode, hint_visible),
            "",
            "",
            "",
            "",
            build_organism_table(example),
            secondary_class,
            elements,
            stylesheet,
            zoom,
            pan,
            layout,
        )
