"""Componentes e textos do painel de jogada."""

from __future__ import annotations

from typing import Any

from dash import html

from frontend.state import ANSWER_OPTIONS


def build_game_answer_panel() -> html.Div:
    """Monta a jogada compacta usada nos modos de desafio e duelo.

    O painel fica junto da árvore para evitar duplicação com uma lateral separada.
    Os IDs foram mantidos para preservar os callbacks existentes.
    """

    return html.Div(
        [
            html.Div(build_sidebar_heading("solo"), id="sidebar-heading", className="inline-game-heading"),
            html.Div(
                [
                    html.Div([html.P(id="selected-element-label"), html.Small(id="selected-element-type")], className="selected-element-card compact-selected-card"),
                    html.Div(
                        [
                            html.Button(option["label"], id={"type": "answer-choice", "value": option["value"]}, n_clicks=0, className="answer-choice")
                            for option in ANSWER_OPTIONS
                        ],
                        id="answer-choice-grid",
                        className="answer-choice-grid inline-answer-choice-grid",
                    ),
                    html.Div(
                        [
                            html.Button("Confirmar resposta", id="submit-answer", n_clicks=0, className="primary-game-button compact-action-button"),
                            html.Button("Limpar seleção", id="clear-selection", n_clicks=0, className="secondary-action-button compact-action-button"),
                            html.Button("Finalizar desafio", id="finish-challenge", n_clicks=0, className="finish-challenge-button compact-action-button"),
                            html.Button("Reiniciar desafio", id="reset-game", n_clicks=0, className="reset-game-button compact-action-button"),
                        ],
                        className="inline-game-actions",
                    ),
                ],
                className="inline-answer-content",
            ),
            html.Div(id="answer-feedback-box", className="feedback-box compact-feedback inline-feedback"),
        ],
        id="answer-panel",
        className="answer-panel inline-answer-panel is-hidden",
    )


def build_game_sidebar() -> html.Aside:
    """Mantém o alvo de layout antigo sem duplicar a jogada na lateral."""

    return html.Aside(id="game-sidebar", className="game-sidebar is-hidden")


def selected_element_text(selected: dict[str, Any] | None) -> tuple[str, str]:
    if not selected:
        return "Nenhum elemento selecionado ainda.", "Clique em um nó ou ligação da árvore."
    if selected["type"] == "edge":
        return "Você selecionou uma ligação evolutiva.", f"Origem: {selected['source']} · Destino: {selected['target']}"
    return f"Você selecionou: {selected['label']}", "Tipo: nó"


def build_sidebar_heading(mode: str) -> html.Div:
    if mode in {"learning", "free"}:
        return html.Div(className="is-hidden")
    return html.Div([html.Span("SUA JOGADA", className="eyebrow"), html.H3("Sua jogada")], className="classification-title")


def sidebar_message(feedback: dict[str, Any] | None) -> str:
    if not feedback:
        return "Selecione um elemento, escolha uma relação e confirme."
    if not feedback.get("answer_record"):
        return feedback.get("message", "Complete a jogada antes de confirmar.")
    if feedback.get("correct"):
        return f"Correto: +{feedback.get('points', 0)} ponto. Veja a correção abaixo."
    return "Incorreto. Veja a correção abaixo."


def build_status_bar(mode: str, example: dict[str, Any], score: int, answers: list[dict[str, Any]], duel_state: dict[str, Any]) -> tuple[list[Any], dict[str, str]]:
    if mode == "learning":
        return [], {"display": "none"}
    if mode == "free":
        return [
            html.Span("Classificação livre", className="mode-badge"),
            html.Span("Sem gabarito automático", className="score-pill"),
            html.Span("Sem pontuação", className="score-pill"),
        ], {}
    total_events = len(example.get("expected_events", []))
    if mode == "solo":
        found = count_found_events(answers)
        return [
            html.Span("Desafio individual", className="mode-badge"),
            html.Span(f"Pontuação: {score}", className="score-pill"),
            html.Span(f"Eventos encontrados: {found} / {total_events}", className="score-pill"),
        ], {}
    found = count_found_events(duel_state.get("answers", []))
    return [
        html.Span("Duelo local", className="mode-badge"),
        html.Span(f"Jogador 1: {duel_state['player_1_score']}", className="score-pill"),
        html.Span(f"Jogador 2: {duel_state['player_2_score']}", className="score-pill"),
        html.Span(f"Vez do Jogador {duel_state['current_player']}", className="turn-indicator"),
        html.Span(f"Progresso: {found} / {total_events}", className="score-pill"),
    ], {}


def count_found_events(answers: list[dict[str, Any]]) -> int:
    return len({answer.get("event_id") for answer in answers if answer.get("correct") and answer.get("event_id")})
