"""Componentes de feedback, correção e revisão."""

from __future__ import annotations

from typing import Any

from dash import html

from src.free_classification import annotation_detail, annotation_identifier, annotation_kind_label, annotation_title
from src.game_rules import describe_events


def build_event_panel(events: list[dict[str, Any]]) -> html.Div:
    described = describe_events(events)
    if not described:
        return html.Div([html.Span("Observação", className="event-icon neutral"), html.P("Este exemplo prioriza a comparação das sequências, sem evento especial.")], className="event-item")
    return html.Div(
        [
            html.Div([html.Span(event["label"], className=f"event-icon event-{event['event_type']}"), html.P(event["description"])], className="event-item")
            for event in described
        ]
    )


def build_answer_feedback(feedback: dict[str, Any] | None, mode: str, reveal: bool) -> html.Div:
    if not feedback:
        return html.Div("Nenhuma jogada corrigida ainda.", className="review-empty-state")
    record = feedback.get("answer_record")
    if not record:
        return html.Div(feedback.get("message", "Complete a jogada para receber feedback."), className="answer-result-panel incorrect")
    if mode == "duel" and not reveal:
        return html.Div(
            [html.H4(feedback.get("message", "Resposta registrada.")), html.P("A explicação completa fica para o final do duelo, para não entregar o gabarito.")],
            className="answer-result-panel compact",
        )
    status = "Correto" if record.get("correct") else "Incorreto"
    return html.Div(
        [
            html.Div("Resultado da jogada", className="eyebrow"),
            html.H4(status),
            html.Div(
                [
                    html.P([html.Strong("Elemento: "), record.get("selected_element_label", "—")]),
                    html.P([html.Strong("Você marcou: "), record.get("player_answer_label", "—")]),
                    html.P([html.Strong("Correto era: "), record.get("correct_answer_label", "—")]),
                ],
                className="answer-summary",
            ),
            html.Div([html.Strong("Por que?"), html.P(record.get("full_explanation", ""))], className="answer-correction"),
            html.Button("Ver no grafo", id={"type": "review-on-graph", "attempt": record.get("attempt_id", "latest")}, n_clicks=0, className="show-on-graph-button"),
        ],
        className="answer-result-panel correct" if record.get("correct") else "answer-result-panel incorrect",
    )


def build_review_cards(attempts: list[dict[str, Any]]) -> list[html.Article | html.Div]:
    if not attempts:
        return [html.Div("Nenhuma tentativa registrada ainda.", className="review-empty-state")]
    cards = []
    for index, attempt in enumerate(attempts, start=1):
        status = "Correto" if attempt.get("correct") else "Incorreto"
        icon = "✓" if attempt.get("correct") else "×"
        player = f" · Jogador {attempt['player_id']}" if attempt.get("player_id") else ""
        cards.append(
            html.Article(
                [
                    html.Div(
                        [
                            html.Span(f"Tentativa {index}{player}", className="review-attempt-label"),
                            html.Span(f"{icon} {status}", className="review-status correct" if attempt.get("correct") else "review-status incorrect"),
                        ],
                        className="review-card-topline",
                    ),
                    html.H4(attempt.get("selected_element_label", "Elemento selecionado")),
                    html.Div(
                        [
                            html.P([html.Strong("Você marcou: "), attempt.get("player_answer_label", "—")]),
                            html.P([html.Strong("Resposta correta: "), attempt.get("correct_answer_label", "—")]),
                        ],
                        className="review-answer-pair",
                    ),
                    html.P(attempt.get("short_feedback", "Tentativa avaliada."), className="review-short-feedback"),
                    html.P(attempt.get("full_explanation", ""), className="review-full-explanation"),
                    html.Button("Ver no grafo", id={"type": "review-on-graph", "attempt": attempt.get("attempt_id", f"attempt_{index}")}, n_clicks=0, className="show-on-graph-button"),
                ],
                className="review-card attempt-review-card correct" if attempt.get("correct") else "review-card attempt-review-card incorrect",
            )
        )
    return cards


def build_results_summary(mode: str, example: dict[str, Any], solo_score: int, submitted: list[dict[str, Any]], duel_state: dict[str, Any]) -> html.Div:
    if mode == "solo":
        heading = f"Pontuação final: {solo_score}"
        attempts = submitted
    else:
        p1 = duel_state["player_1_score"]
        p2 = duel_state["player_2_score"]
        heading = f"Empate em {p1} ponto(s)" if p1 == p2 else f"Vencedor: Jogador {1 if p1 > p2 else 2}"
        attempts = duel_state.get("answers", [])
    return html.Div(
        [
            html.Div("Revisão da rodada", className="eyebrow"),
            html.H3(heading),
            html.P("Confira cada tentativa, veja o elemento relacionado no grafo e entenda o motivo da correção.", className="review-intro"),
            build_graph_highlight_legend(),
            html.Div(build_review_cards(attempts), className="round-review-list attempt-review-grid"),
            html.Details([html.Summary("Ver explicação geral do exemplo"), html.P(example["explanation"]), build_event_panel(example["expected_events"])], className="accordion-section review-explanation-details"),
        ],
        className="interpretation-box round-review-section",
    )


def build_correction_section(feedback: dict[str, Any] | None, mode: str, reveal: bool, summary: html.Div | None) -> html.Div | str:
    if mode == "learning":
        return ""
    return html.Section(
        [
            html.Div(
                [
                    html.Div("Revisão da jogada", className="eyebrow"),
                    html.H3("Correção e revisão"),
                    html.P("Entenda seus acertos, erros e veja os elementos destacados no grafo.", className="review-intro"),
                ],
                className="correction-heading",
            ),
            html.Div(summary if summary else build_answer_feedback(feedback, mode, reveal), className="answer-review-area graph-explanation-panel correction-content-grid"),
        ],
        className="correction-section game-correction-section",
    )


def build_graph_highlight_legend() -> html.Div:
    return html.Div(
        [
            html.Span([html.I(className="review-dot primary"), "Elemento correto principal"]),
            html.Span([html.I(className="review-dot related"), "Elementos relacionados"]),
            html.Span([html.I(className="review-dot wrong"), "Sua marcação incorreta"]),
            html.Span([html.I(className="review-dot missed"), "Resposta correta perdida"]),
        ],
        className="graph-highlight-legend",
    )


def build_free_annotations_section(annotations: list[dict[str, Any]]) -> html.Section:
    return html.Section(
        [
            html.Div(
                [
                    html.Div("Anotações livres", className="eyebrow"),
                    html.H3("Relações criadas e classificações"),
                    html.P("Essas marcações são interpretativas. O app não corrige nem pontua este modo.", className="review-intro"),
                ],
                className="correction-heading",
            ),
            html.Div(build_free_annotation_cards(annotations), className="free-annotation-list"),
        ],
        className="correction-section game-correction-section free-annotation-section",
    )


def build_free_annotation_cards(annotations: list[dict[str, Any]]) -> list[Any]:
    if not annotations:
        return [html.Div("Nenhuma classificação ou relação especial criada ainda.", className="review-empty-state")]

    cards: list[Any] = []
    for annotation in annotations:
        annotation_id = annotation_identifier(annotation)
        cards.append(
            html.Article(
                [
                    html.Div(
                        [
                            html.Span(annotation_kind_label(annotation), className="review-attempt-label"),
                            html.Button("Remover", id={"type": "remove-user-annotation", "id": annotation_id}, n_clicks=0, className="remove-annotation-button"),
                        ],
                        className="review-card-topline",
                    ),
                    html.H4(annotation_title(annotation)),
                    html.P(annotation_detail(annotation), className="review-full-explanation"),
                ],
                className=f"review-card free-annotation-card {annotation.get('relation_type', '')}",
            )
        )
    return cards

