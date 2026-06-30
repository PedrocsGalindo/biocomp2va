"""EvoRamos: MVP educativo para interpretar árvores filogenéticas.

Este arquivo concentra a interface Dash de forma propositalmente simples. O projeto
é experimental, então a organização prioriza leitura e facilidade para ajustes.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import dash_cytoscape as cyto
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update

from src.cytoscape_elements import build_cytoscape_elements
from src.example_loader import get_example_by_id, load_examples
from src.game_rules import check_player_answer, describe_events, event_name
from src.tree_builder import build_example_graph

# -----------------------------------------------------------------------------
# Dados fixos de interface
# -----------------------------------------------------------------------------

CONCEPTS = [
    ("DNA", "O DNA armazena a informação genética dos organismos. Aqui, ele é representado pelas letras A, T, C e G.", "DNA"),
    ("Sequência genética", "É a ordem das bases do DNA. Quanto mais parecidas duas sequências, maior pode ser a proximidade evolutiva.", "SEQ"),
    ("Mutação", "É uma alteração na sequência genética. Pequenas mudanças acumuladas ajudam a diferenciar espécies ao longo do tempo.", "MUT"),
    ("Árvore filogenética", "Representa relações evolutivas, proximidades, ancestrais comuns e separações entre linhagens.", "TREE"),
    ("Especiação", "É o surgimento de novas espécies a partir de uma linhagem ancestral, geralmente mostrado por uma bifurcação.", "SP"),
    ("Hibridização", "Ocorre quando uma linhagem recebe contribuição genética de duas linhagens diferentes.", "HYB"),
    ("Transferência horizontal", "Material genético passa entre organismos sem relação direta de ancestralidade.", "HGT"),
]

GAME_MODES = {
    "learning": "Aprendizado",
    "solo": "Desafio individual",
    "duel": "Duelo local",
}

ANSWER_OPTIONS = [
    {"label": "Especiação", "value": "speciation"},
    {"label": "Hibridização", "value": "hybridization"},
    {"label": "Transferência horizontal", "value": "horizontal_transfer"},
    {"label": "Não é evento especial", "value": "none"},
]

EMPTY_DUEL_STATE = {
    "current_player": 1,
    "player_1_score": 0,
    "player_2_score": 0,
    "answers": [],
}

DEFAULT_TREE_LAYOUT = {
    "name": "breadthfirst",
    "directed": True,
    "spacingFactor": 1.55,
    "padding": 38,
    "animate": True,
    "fit": True,
}

BASE_NODE_STYLE = {
    "label": "data(label)",
    "font-family": "Inter, sans-serif",
    "font-size": "13px",
    "font-weight": "600",
    "text-wrap": "wrap",
    "text-max-width": "125px",
    "text-valign": "bottom",
    "text-margin-y": "9px",
    "color": "#f3efe4",
    "text-outline-color": "#071311",
    "text-outline-width": 2,
    "border-width": 2,
    "width": 42,
    "height": 42,
}

TREE_STYLESHEET_LEARNING = [
    {"selector": "node", "style": BASE_NODE_STYLE},
    {"selector": ".organism-node", "style": {"background-color": "#145c4c", "border-color": "#54f0c2"}},
    {"selector": ".internal-node", "style": {"background-color": "#6d385c", "border-color": "#c58aaf", "shape": "diamond", "width": 30, "height": 30, "font-size": "11px"}},
    {"selector": ".speciation-node", "style": {"background-color": "#147a65", "border-color": "#78f2c4", "border-width": 4}},
    {"selector": ".hybrid-node", "style": {"background-color": "#6d385c", "border-color": "#dba5ca", "border-width": 4}},
    {"selector": "edge", "style": {"curve-style": "bezier", "width": 3, "line-color": "#58756c", "target-arrow-color": "#58756c", "color": "#c5d2cb", "font-size": "10px", "label": "data(label)", "text-background-color": "#071311", "text-background-opacity": 0.88, "text-background-padding": "3px"}},
    {"selector": ".hybrid-edge", "style": {"line-color": "#b66b9a", "target-arrow-color": "#b66b9a", "target-arrow-shape": "triangle", "width": 4}},
    {"selector": ".transfer-edge", "style": {"line-color": "#e2687d", "target-arrow-color": "#e2687d", "target-arrow-shape": "triangle", "line-style": "dashed", "width": 4}},
]

TREE_STYLESHEET_GAME = [
    {"selector": "node", "style": BASE_NODE_STYLE},
    {"selector": ".organism-node", "style": {"background-color": "#173731", "border-color": "#7fb0a0"}},
    {"selector": ".internal-node", "style": {"background-color": "#324742", "border-color": "#93aca3", "shape": "diamond", "width": 30, "height": 30, "font-size": "11px"}},
    {"selector": ".speciation-node", "style": {"background-color": "#324742", "border-color": "#93aca3", "border-width": 2}},
    {"selector": ".hybrid-node", "style": {"background-color": "#324742", "border-color": "#93aca3", "border-width": 2}},
    {"selector": "edge", "style": {"curve-style": "bezier", "width": 3.5, "line-color": "#6d827c", "target-arrow-color": "#6d827c", "label": ""}},
    {"selector": ".hybrid-edge", "style": {"line-color": "#91a39c", "target-arrow-color": "#91a39c", "target-arrow-shape": "triangle", "width": 4.5}},
    {"selector": ".transfer-edge", "style": {"line-color": "#91a39c", "target-arrow-color": "#91a39c", "target-arrow-shape": "triangle", "line-style": "dashed", "width": 4.5}},
]

EXAMPLES = load_examples()
FIRST_EXAMPLE = EXAMPLES[0]

# -----------------------------------------------------------------------------
# Helpers visuais pequenos
# -----------------------------------------------------------------------------


def build_concept_card(index: int, slot: str) -> html.Article:
    title, description, icon = CONCEPTS[index]
    active = slot == "active"
    return html.Article(
        [
            html.Div([
                html.Div(icon, className="concept-icon", **{"aria-hidden": "true"}),
                html.Span(f"{index + 1} de {len(CONCEPTS)}", className="concept-position"),
            ], className="concept-card-topline"),
            html.H3(title),
            html.P(description),
        ],
        className="concept-carousel-card concept-card-active" if active else f"concept-carousel-card concept-card-preview {slot}",
        **{"aria-hidden": "false" if active else "true"},
    )


def build_concept_carousel(index: int) -> html.Div:
    return html.Div(
        html.Div([
            build_concept_card((index - 1) % len(CONCEPTS), "left"),
            build_concept_card(index, "active"),
            build_concept_card((index + 1) % len(CONCEPTS), "right"),
        ], className="concept-carousel-track"),
        className="concept-carousel-content",
    )


def build_mode_selector(active_mode: str) -> html.Div:
    return html.Div(
        [
            html.Button(label, id=f"mode-{mode_id}", n_clicks=0, className="mode-card is-active" if mode_id == active_mode else "mode-card")
            for mode_id, label in GAME_MODES.items()
        ],
        className="mode-selector",
    )


def build_exercise_cards(selected_id: str) -> list[html.Button]:
    cards: list[html.Button] = []
    for index, example in enumerate(EXAMPLES, start=1):
        active = example["id"] == selected_id
        cards.append(
            html.Button(
                [
                    html.Div([
                        html.Span(f"Exercício {index}", className="eyebrow"),
                        html.Span(example["difficulty"], className=f"difficulty-badge difficulty-{example['difficulty'].lower()}"),
                    ], className="card-topline"),
                    html.H3(example["title"]),
                    html.P(example["description"]),
                ],
                id={"type": "exercise-card", "index": example["id"]},
                n_clicks=0,
                className="exercise-card is-active" if active else "exercise-card",
            )
        )
    return cards


def build_organism_table(example: dict[str, Any]) -> html.Div:
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th("Organismo"), html.Th("DNA"), html.Th("Descrição")])),
                html.Tbody([
                    html.Tr([html.Td(org["name"]), html.Td(html.Code(org["sequence"])), html.Td(org["description"])])
                    for org in example["organisms"]
                ]),
            ],
            className="organism-table",
        ),
        className="table-wrapper",
    )


def build_event_panel(events: list[dict[str, Any]]) -> html.Div:
    described = describe_events(events)
    if not described:
        return html.Div([html.Span("Observação", className="event-icon neutral"), html.P("Este exemplo prioriza a comparação das sequências, sem evento especial.")], className="event-item")
    return html.Div([
        html.Div([html.Span(event["label"], className=f"event-icon event-{event['event_type']}"), html.P(event["description"])], className="event-item")
        for event in described
    ])


def build_legend(mode: str) -> html.Div:
    if mode == "learning":
        items = [
            html.Span([html.I(className="legend-dot organism"), "Organismo"]),
            html.Span([html.I(className="legend-dot ancestor"), "Ancestral"]),
            html.Span([html.I(className="legend-line hybrid"), "Hibridização"]),
            html.Span([html.I(className="legend-line transfer"), "Transferência horizontal"]),
        ]
    else:
        items = [
            html.Span([html.I(className="legend-dot organism neutral"), "Organismo"]),
            html.Span([html.I(className="legend-dot ancestor neutral"), "Ancestral"]),
            html.Span([html.I(className="legend-line neutral"), "Relação evolutiva"]),
            html.Span([html.I(className="legend-line special"), "Ligação especial"]),
        ]
    return html.Div(items, className="legend")


def build_instructions_strip(mode: str, hint_visible: bool = False) -> html.Div:
    text = {
        "learning": "Explore a árvore. Use a lâmpada para abrir uma leitura guiada quando precisar.",
        "solo": "Clique em um nó ou ligação da árvore, escolha a relação evolutiva e confirme sua resposta.",
        "duel": "Na sua vez, clique em um elemento da árvore, escolha a relação e confirme a jogada.",
    }[mode]
    hint_class = "hint-button is-active" if hint_visible else "hint-button"
    hint_title = "Esconder dica" if hint_visible else "Abrir dica"
    return html.Div(
        [
            html.P([html.Strong("Como usar: "), text], className="game-instructions-text"),
            html.Button("💡", id="show-interpretation", n_clicks=0, className=hint_class, title=hint_title),
        ],
        className="game-instructions-strip",
    )


def build_guided_hint(example: dict[str, Any], mode: str, visible: bool) -> html.Div:
    if mode == "learning":
        title = "Leitura guiada"
        text = example["explanation"]
        tip = "Compare as sequências, siga os ramos e observe onde surgem eventos evolutivos."
    else:
        title = "Dica"
        text = "Observe se você clicou em um nó interno, em uma ligação comum ou em uma ligação especial entre ramos."
        tip = "A dica ajuda a classificar o elemento, mas não revela o gabarito."
    return html.Div(
        [html.Div(title, className="eyebrow"), html.H3(title), html.P(text), html.P(tip, className="interpretation-tip")],
        className="guided-reading-box" + ("" if visible else " is-hidden"),
    )


def selected_element_text(selected: dict[str, Any] | None) -> tuple[str, str]:
    if not selected:
        return "Nenhum elemento selecionado ainda.", "Clique em um nó ou ligação da árvore."
    if selected["type"] == "edge":
        return "Você selecionou uma ligação evolutiva.", f"Origem: {selected['source']} · Destino: {selected['target']}"
    return f"Você selecionou: {selected['label']}", "Tipo: nó"


def build_status_bar(mode: str, example: dict[str, Any], score: int, answers: list[dict[str, Any]], duel_state: dict[str, Any]) -> tuple[list[Any], dict[str, str]]:
    if mode == "learning":
        return [], {"display": "none"}
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


def sidebar_message(feedback: dict[str, Any] | None) -> str:
    if not feedback:
        return "Selecione um elemento, escolha uma relação e confirme."
    if not feedback.get("answer_record"):
        return feedback.get("message", "Complete a jogada antes de confirmar.")
    if feedback.get("correct"):
        return f"Correto: +{feedback.get('points', 0)} ponto. Veja a correção abaixo."
    return "Incorreto. Veja a correção abaixo."


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
            html.Div([
                html.P([html.Strong("Elemento: "), record.get("selected_element_label", "—")]),
                html.P([html.Strong("Você marcou: "), record.get("player_answer_label", "—")]),
                html.P([html.Strong("Correto era: "), record.get("correct_answer_label", "—")]),
            ], className="answer-summary"),
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
                    html.Div([
                        html.Span(f"Tentativa {index}{player}", className="review-attempt-label"),
                        html.Span(f"{icon} {status}", className="review-status correct" if attempt.get("correct") else "review-status incorrect"),
                    ], className="review-card-topline"),
                    html.H4(attempt.get("selected_element_label", "Elemento selecionado")),
                    html.Div([
                        html.P([html.Strong("Você marcou: "), attempt.get("player_answer_label", "—")]),
                        html.P([html.Strong("Resposta correta: "), attempt.get("correct_answer_label", "—")]),
                    ], className="review-answer-pair"),
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
            html.Div([
                html.Div("Revisão da jogada", className="eyebrow"),
                html.H3("Correção e revisão"),
                html.P("Entenda seus acertos, erros e veja os elementos destacados no grafo.", className="review-intro"),
            ], className="correction-heading"),
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

# -----------------------------------------------------------------------------
# Árvore e estilos Cytoscape
# -----------------------------------------------------------------------------


def build_tree_stylesheet(mode: str, reveal: bool, selected: dict[str, Any] | None, highlight: dict[str, list[str]] | None) -> list[dict[str, Any]]:
    stylesheet = list(TREE_STYLESHEET_LEARNING if mode == "learning" or reveal else TREE_STYLESHEET_GAME)
    if selected:
        element_id = selected.get("id")
        if selected.get("type") == "node":
            stylesheet.append({"selector": f'node[id = "{element_id}"]', "style": {"border-color": "#54f0c2", "border-width": 5, "shadow-blur": 22, "shadow-color": "#2ee6bd", "shadow-opacity": 0.65, "shadow-offset-x": 0, "shadow-offset-y": 0}})
        else:
            stylesheet.append({"selector": f'edge[id = "{element_id}"]', "style": {"line-color": "#54f0c2", "target-arrow-color": "#54f0c2", "width": 6, "shadow-blur": 22, "shadow-color": "#2ee6bd", "shadow-opacity": 0.65}})
    if highlight:
        stylesheet.extend(build_review_highlight_styles(highlight))
    return stylesheet


def build_review_highlight_styles(highlight: dict[str, list[str]]) -> list[dict[str, Any]]:
    specs = [
        ("primary_nodes", "node", "#78f2c4", 36),
        ("primary_edges", "edge", "#78f2c4", 36),
        ("related_nodes", "node", "#59bdf7", 24),
        ("related_edges", "edge", "#59bdf7", 24),
        ("wrong_nodes", "node", "#ff6b7a", 30),
        ("wrong_edges", "edge", "#ff6b7a", 30),
        ("missed_nodes", "node", "#f6b44b", 28),
        ("missed_edges", "edge", "#f6b44b", 28),
    ]
    styles = []
    for key, element_type, color, glow in specs:
        for element_id in highlight.get(key, []) or []:
            if element_type == "node":
                styles.append({"selector": f'node[id = "{element_id}"]', "style": {"background-color": color, "border-color": color, "border-width": 5, "shadow-blur": glow, "shadow-color": color, "shadow-opacity": 0.72}})
            else:
                styles.append({"selector": f'edge[id = "{element_id}"]', "style": {"line-color": color, "target-arrow-color": color, "width": 6, "shadow-blur": glow, "shadow-color": color, "shadow-opacity": 0.72, "z-index": 999}})
    return styles


def tree_payload(example: dict[str, Any], mode: str, reveal: bool, selected: dict[str, Any] | None, highlight: dict[str, list[str]] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    graph = build_example_graph(example)
    return build_cytoscape_elements(graph), build_tree_stylesheet(mode, reveal, selected, highlight)


def current_attempts(mode: str, submitted: list[dict[str, Any]], duel_state: dict[str, Any]) -> list[dict[str, Any]]:
    return duel_state.get("answers", []) if mode == "duel" else submitted

# -----------------------------------------------------------------------------
# Layout base
# -----------------------------------------------------------------------------

app = Dash(__name__, title="EvoRamos", update_title="Carregando...")
server = app.server

app.layout = html.Main(
    [
        dcc.Store(id="concept-index", data=0),
        dcc.Store(id="selected-example-id", data=FIRST_EXAMPLE["id"]),
        dcc.Store(id="game-mode", data="learning"),
        dcc.Store(id="selected-tree-element", data=None),
        dcc.Store(id="selected-answer-choice", data=None),
        dcc.Store(id="submitted-answers", data=[]),
        dcc.Store(id="solo-score", data=0),
        dcc.Store(id="duel-state", data=deepcopy(EMPTY_DUEL_STATE)),
        dcc.Store(id="answer-feedback", data=None),
        dcc.Store(id="reveal-results", data=False),
        dcc.Store(id="review-highlight", data=None),
        dcc.Store(id="guided-reading-visible", data=False),
        dcc.Store(id="tree-zoom", data=1.0),
        dcc.Store(id="tree-pan", data={"x": 0, "y": 0}),
        dcc.Store(id="tree-layout-seed", data=0),

        html.Header(
            [
                html.Div([
                    html.Span("BIOLOGIA + TECNOLOGIA", className="hero-kicker"),
                    html.H1(["Evo", html.Span("Ramos")]),
                    html.H2("Interprete árvores filogenéticas em modo aula, desafio e duelo."),
                    html.P("Compare sequências fictícias de DNA, explore relações evolutivas e descubra como diferentes eventos aparecem em uma árvore."),
                    html.A("Começar pelos exercícios", href="#exercicios", className="hero-button"),
                ], className="hero-content"),
                html.Div([html.Div(base, className=f"dna-base base-{base.lower()}") for base in ["A", "T", "C", "G"]], className="hero-visual"),
            ],
            className="hero",
        ),

        html.Section(
            [
                html.Div([html.Span("BASES PARA EXPLORAR", className="eyebrow"), html.H2(["Conceitos ", html.Span("biológicos"), " essenciais"]), html.P("Explore os principais conceitos antes de interpretar os ramos.")], className="section-heading"),
                html.Div([
                    html.Button("Anterior", id="previous-concept", n_clicks=0, className="carousel-button"),
                    html.Div(build_concept_carousel(0), id="concept-carousel-card", className="concept-carousel-stage"),
                    html.Button("Próximo", id="next-concept", n_clicks=0, className="carousel-button"),
                ], className="concept-carousel"),
            ],
            className="content-section concept-carousel-section",
        ),

        html.Section(
            [
                html.Div([html.Span("PRÁTICA GUIADA", className="eyebrow"), html.H2("Exercícios prontos"), html.P("Escolha um cenário e mude entre aprendizado, desafio e duelo local.")], className="section-heading"),
                html.Div(build_mode_selector("learning"), id="mode-selector-wrapper"),
                html.Div(build_exercise_cards(FIRST_EXAMPLE["id"]), id="exercise-card-grid", className="exercise-grid"),
            ],
            className="content-section",
            id="exercicios",
        ),

        html.Section(
            [
                html.Div(id="game-status-bar", className="game-status-bar"),
                html.Div(id="game-instructions-shell"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div([
                                    html.Button("+", id="tree-zoom-in", n_clicks=0, className="tree-control-button", title="Ampliar"),
                                    html.Button("−", id="tree-zoom-out", n_clicks=0, className="tree-control-button", title="Reduzir"),
                                    html.Button("⦿", id="tree-reset-view", n_clicks=0, className="tree-control-button", title="Recentralizar"),
                                ], className="tree-toolbar-actions"),
                                html.Div(id="legend-wrapper"),
                                html.Div(id="interpretation-panel"),
                                cyto.Cytoscape(
                                    id="phylogenetic-tree",
                                    elements=[],
                                    layout=DEFAULT_TREE_LAYOUT,
                                    zoom=1.0,
                                    pan={"x": 0, "y": 0},
                                    minZoom=0.45,
                                    maxZoom=2.2,
                                    stylesheet=TREE_STYLESHEET_LEARNING,
                                    responsive=True,
                                    className="tree-canvas",
                                ),
                            ],
                            id="tree-column",
                            className="game-tree-column",
                        ),
                        html.Aside(
                            [
                                html.Div([html.Span("SUA JOGADA", className="eyebrow"), html.H3("Sua jogada")]),
                                html.Div([
                                    html.Div([html.P(id="selected-element-label"), html.Small(id="selected-element-type")], className="selected-element-card"),
                                    html.Div([html.Button(option["label"], id={"type": "answer-choice", "value": option["value"]}, n_clicks=0, className="answer-choice") for option in ANSWER_OPTIONS], id="answer-choice-grid", className="answer-choice-grid"),
                                    html.Button("Confirmar resposta", id="submit-answer", n_clicks=0, className="primary-game-button"),
                                    html.Button("Limpar seleção", id="clear-selection", n_clicks=0, className="secondary-action-button"),
                                    html.Button("Finalizar desafio", id="finish-challenge", n_clicks=0, className="finish-challenge-button"),
                                    html.Button("Reiniciar desafio", id="reset-game", n_clicks=0, className="reset-game-button"),
                                    html.Div(id="answer-feedback-box", className="feedback-box"),
                                ], id="answer-panel", className="answer-panel"),
                            ],
                            id="game-sidebar",
                            className="game-sidebar",
                        ),
                        html.Div(id="results-summary", className="game-correction-section"),
                    ],
                    id="main-game-layout",
                    className="game-layout",
                ),
                html.Div(
                    [
                        html.Div(id="learning-goal", className="info-box"),
                        html.Div([
                            html.Details([html.Summary("Ver organismos e sequências"), html.Div(id="organism-table")], className="accordion-section"),
                            html.Details([html.Summary("Ver objetivo de aprendizagem"), html.Div(id="secondary-goal-copy")], className="accordion-section"),
                            html.Details([html.Summary("Ver descrição do exemplo"), html.Div(id="secondary-description")], className="accordion-section"),
                            html.Details([html.Summary("Ver explicação final"), html.Div(id="secondary-explanation")], className="accordion-section"),
                        ], className="secondary-content-tabs"),
                    ],
                    id="secondary-content",
                ),
            ],
            className="example-shell",
        ),
    ],
    className="page",
)

# -----------------------------------------------------------------------------
# Callbacks pequenos e independentes
# -----------------------------------------------------------------------------


@app.callback(Output("concept-index", "data"), Input("previous-concept", "n_clicks"), Input("next-concept", "n_clicks"), State("concept-index", "data"), prevent_initial_call=True)
def update_concept_index(_previous: int, _next: int, current_index: int) -> int:
    step = -1 if ctx.triggered_id == "previous-concept" else 1
    return (current_index + step) % len(CONCEPTS)


@app.callback(Output("concept-carousel-card", "children"), Input("concept-index", "data"))
def render_concepts(index: int) -> html.Div:
    return build_concept_carousel(index)


@app.callback(Output("game-mode", "data"), Input("mode-learning", "n_clicks"), Input("mode-solo", "n_clicks"), Input("mode-duel", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
def select_mode(_learning: int, _solo: int, _duel: int, current: str) -> str:
    return ctx.triggered_id.replace("mode-", "") if ctx.triggered_id else current


@app.callback(Output("mode-learning", "className"), Output("mode-solo", "className"), Output("mode-duel", "className"), Input("game-mode", "data"))
def update_mode_classes(active: str) -> tuple[str, str, str]:
    return tuple("mode-card is-active" if mode == active else "mode-card" for mode in GAME_MODES)


@app.callback(Output("selected-example-id", "data"), Input({"type": "exercise-card", "index": ALL}, "n_clicks"), State("selected-example-id", "data"), prevent_initial_call=True)
def select_example(_clicks: list[int], current: str) -> str:
    return ctx.triggered_id.get("index") if ctx.triggered_id else current


@app.callback(Output({"type": "exercise-card", "index": ALL}, "className"), Input("selected-example-id", "data"))
def update_exercise_classes(selected_id: str) -> list[str]:
    return ["exercise-card is-active" if example["id"] == selected_id else "exercise-card" for example in EXAMPLES]


@app.callback(Output("selected-answer-choice", "data"), Input({"type": "answer-choice", "value": ALL}, "n_clicks"), State("selected-answer-choice", "data"), prevent_initial_call=True)
def select_answer(_clicks: list[int], current: str | None) -> str | None:
    return ctx.triggered_id.get("value") if ctx.triggered_id else current


@app.callback(Output({"type": "answer-choice", "value": ALL}, "className"), Input("selected-answer-choice", "data"))
def update_answer_classes(selected: str | None) -> list[str]:
    return ["answer-choice is-selected" if option["value"] == selected else "answer-choice" for option in ANSWER_OPTIONS]


@app.callback(Output("selected-tree-element", "data"), Input("phylogenetic-tree", "tapNodeData"), Input("phylogenetic-tree", "tapEdgeData"), prevent_initial_call=True)
def select_tree_element(node_data: dict[str, Any] | None, edge_data: dict[str, Any] | None) -> dict[str, Any] | None:
    if not ctx.triggered:
        return no_update
    prop = ctx.triggered[0]["prop_id"].split(".")[-1]
    if prop == "tapNodeData" and node_data:
        return {"id": node_data["id"], "label": node_data.get("label", node_data["id"]), "type": "node"}
    if prop == "tapEdgeData" and edge_data:
        return {"id": edge_data["id"], "label": edge_data.get("label") or "Ligação evolutiva", "type": "edge", "source": edge_data["source"], "target": edge_data["target"]}
    return no_update


@app.callback(Output("selected-tree-element", "data", allow_duplicate=True), Output("selected-answer-choice", "data", allow_duplicate=True), Input("clear-selection", "n_clicks"), prevent_initial_call=True)
def clear_selection(_clicks: int) -> tuple[None, None]:
    return None, None


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


@app.callback(
    Output("selected-tree-element", "data", allow_duplicate=True),
    Output("selected-answer-choice", "data", allow_duplicate=True),
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
def reset_game(_example_id: str, _mode: str, _reset_clicks: int) -> tuple[None, None, list[dict[str, Any]], int, dict[str, Any], None, bool, None, bool, float, dict[str, int]]:
    return None, None, [], 0, deepcopy(EMPTY_DUEL_STATE), None, False, None, False, 1.0, {"x": 0, "y": 0}


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
    prevent_initial_call=True,
)
def submit_answer(_clicks: int, example_id: str, mode: str, selected: dict[str, Any] | None, answer_type: str | None, submitted: list[dict[str, Any]], score: int, duel_state: dict[str, Any]):
    example = get_example_by_id(EXAMPLES, example_id)
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

# -----------------------------------------------------------------------------
# Render principal: uma única callback monta a tela a partir dos estados.
# -----------------------------------------------------------------------------


@app.callback(
    Output("game-status-bar", "children"),
    Output("game-status-bar", "style"),
    Output("game-instructions-shell", "children"),
    Output("main-game-layout", "className"),
    Output("tree-column", "className"),
    Output("game-sidebar", "className"),
    Output("selected-element-label", "children"),
    Output("selected-element-type", "children"),
    Output("finish-challenge", "children"),
    Output("reset-game", "children"),
    Output("answer-feedback-box", "children"),
    Output("answer-feedback-box", "className"),
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
    Input("game-mode", "data"),
    Input("selected-tree-element", "data"),
    Input("selected-answer-choice", "data"),
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
def render_app_state(example_id: str, mode: str, selected: dict[str, Any] | None, answer_choice: str | None, submitted: list[dict[str, Any]], score: int, duel_state: dict[str, Any], feedback: dict[str, Any] | None, reveal: bool, highlight: dict[str, list[str]] | None, hint_visible: bool, zoom: float, pan: dict[str, int], layout_seed: int):
    example = get_example_by_id(EXAMPLES, example_id)
    elements, stylesheet = tree_payload(example, mode, reveal, selected, highlight)
    status_children, status_style = build_status_bar(mode, example, score, submitted, duel_state)
    selected_label, selected_type = selected_element_text(selected)
    sidebar_feedback = sidebar_message(feedback)
    feedback_class = "feedback-box"
    if feedback:
        feedback_class += " correct" if feedback.get("correct") else " incorrect"

    layout_class = "game-layout learning-layout" if mode == "learning" else "game-layout is-game-mode"
    tree_class = "game-tree-column is-learning learning-full-width" if mode == "learning" else "game-tree-column is-game-mode"
    sidebar_class = "game-sidebar is-learning is-hidden" if mode == "learning" else "game-sidebar is-game-mode"
    secondary_class = "secondary-content-stack" + (" is-game-mode" if mode != "learning" else "")
    finish_label = "Encerrar duelo" if mode == "duel" else "Finalizar desafio"
    reset_label = "Reiniciar duelo" if mode == "duel" else "Reiniciar desafio"
    summary = build_results_summary(mode, example, score, submitted, duel_state) if mode != "learning" and reveal else None
    correction = build_correction_section(feedback, mode, reveal, summary)
    explanation_text = example["explanation"] if mode == "learning" or reveal else "Finalize o modo atual para revelar a explicação completa."
    layout = {**DEFAULT_TREE_LAYOUT, "padding": 38 + (layout_seed % 2)}

    return (
        status_children,
        status_style,
        build_instructions_strip(mode, hint_visible),
        layout_class,
        tree_class,
        sidebar_class,
        selected_label,
        selected_type,
        finish_label,
        reset_label,
        sidebar_feedback,
        feedback_class,
        correction,
        build_legend(mode if not reveal else "learning"),
        build_guided_hint(example, mode, hint_visible),
        [html.Strong("Objetivo de aprendizagem"), html.P(example["learning_goal"])],
        [html.Strong("Objetivo de aprendizagem"), html.P(example["learning_goal"])],
        html.P(example["description"]),
        html.P(explanation_text),
        build_organism_table(example),
        secondary_class,
        elements,
        stylesheet,
        zoom,
        pan,
        layout,
    )


if __name__ == "__main__":
    app.run(debug=True)
