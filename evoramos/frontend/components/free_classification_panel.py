"""Painel compacto de classificação livre."""

from __future__ import annotations

from typing import Any

from dash import html

from frontend.state import FREE_CLASSIFICATION_OPTIONS, SPECIAL_RELATION_OPTIONS
from frontend.components.game_sidebar import selected_element_text
from src.free_classification import classification_label


def build_free_classification_panel() -> html.Div:
    """Monta uma barra compacta para classificar e criar relações no modo livre.

    A lógica fica em dois modos:
    - Classificar elemento: clique em um nó/aresta, escolha a classificação e aplique.
    - Criar relação especial: escolha o tipo e clique em dois nós; a relação nasce automaticamente.
    """

    return html.Div(
        [
            html.Div(
                [
                    html.Div([html.Span("SUA JOGADA", className="eyebrow"), html.H3("Sua jogada")], className="classification-title"),
                    html.Div(
                        [
                            html.Button("Classificar elemento", id="free-mode-classify", n_clicks=0, className="classification-tab is-active"),
                            html.Button("Criar relação especial", id="free-mode-create-relation", n_clicks=0, className="classification-tab"),
                        ],
                        className="classification-tabs compact-tabs",
                    ),
                ],
                className="classification-compact-header",
            ),
            html.Div(
                [
                    html.Div([html.P(id="free-selected-element-label"), html.Small(id="free-selected-element-type")], className="selected-element-card compact-selected-card"),
                    html.Div(
                        [
                            html.Button(option["label"], id={"type": "free-classification-choice", "value": option["value"]}, n_clicks=0, className="answer-choice")
                            for option in FREE_CLASSIFICATION_OPTIONS
                        ],
                        className="answer-choice-grid free-choice-grid compact-choice-grid",
                    ),
                    html.Div(
                        [
                            html.Button("Aplicar", id="apply-classification", n_clicks=0, className="primary-game-button compact-action-button"),
                            html.Button("Remover", id="remove-classification", n_clicks=0, className="secondary-action-button compact-action-button"),
                        ],
                        className="classification-inline-actions",
                    ),
                ],
                id="free-classify-panel",
                className="classification-section compact-classify-flow",
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Button(option["label"], id={"type": "special-relation-choice", "value": option["value"]}, n_clicks=0, className="answer-choice")
                            for option in SPECIAL_RELATION_OPTIONS
                        ],
                        className="answer-choice-grid free-choice-grid compact-choice-grid relation-type-grid",
                    ),
                    html.P("Escolha o tipo e clique no nó de origem, depois no nó de destino. A relação será criada automaticamente.", className="classification-help-text relation-help"),
                    html.Div(id="free-relation-progress", className="relation-progress-pill"),
                    html.Button("Cancelar", id="cancel-relation", n_clicks=0, className="secondary-action-button compact-action-button compact-cancel-button"),
                    # Mantidos como elementos ocultos para preservar os callbacks existentes de renderização.
                    html.Div([html.P(id="free-draft-source"), html.P(id="free-draft-target"), html.P(id="free-draft-type")], className="is-hidden"),
                ],
                id="free-relation-panel",
                className="classification-section special-relation-flow is-hidden",
            ),
            html.Div(id="free-feedback-box", className="feedback-box compact-feedback"),
        ],
        id="free-panel",
        className="classification-panel is-hidden compact-free-panel",
    )


def free_selected_element_text(selected: dict[str, Any] | None, selected_classification: str | None) -> tuple[str, str]:
    label, element_type = selected_element_text(selected)
    if selected_classification:
        return label, f"{element_type} · Escolha: {classification_label(selected_classification)}"
    return label, element_type


def build_free_feedback(feedback: dict[str, Any] | None) -> tuple[str, str]:
    if not feedback:
        return "Clique em um elemento para classificar ou entre em criação de relação especial.", "feedback-box compact-feedback"
    feedback_type = feedback.get("type", "info")
    class_name = "feedback-box compact-feedback"
    if feedback_type == "success":
        class_name += " correct"
    elif feedback_type == "error":
        class_name += " incorrect"
    return feedback.get("message", ""), class_name


def build_relation_progress(draft: dict[str, Any] | None) -> str:
    current = draft or {}
    relation_type = current.get("relation_type")
    source = current.get("source") or {}
    target = current.get("target") or {}
    relation = "tipo não escolhido" if not relation_type else next(
        (option["label"] for option in SPECIAL_RELATION_OPTIONS if option["value"] == relation_type),
        relation_type,
    )
    source_label = source.get("label") if isinstance(source, dict) else None
    target_label = target.get("label") if isinstance(target, dict) else None
    if not source_label:
        return f"{relation} · clique no nó de origem."
    if not target_label:
        return f"{relation} · origem: {source_label} · agora clique no destino."
    return f"{relation} · {source_label} → {target_label}."
