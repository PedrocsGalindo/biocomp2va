"""Interface principal do EvoRamos com modos de aprendizado e jogo."""

from __future__ import annotations

from typing import Any

import dash_cytoscape as cyto
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update

from src.cytoscape_elements import build_cytoscape_elements
from src.example_loader import get_example_by_id, load_examples
from src.game_rules import check_player_answer, describe_events
from src.tree_builder import build_example_graph


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
    "padding": 45,
    "animate": True,
    "fit": True,
}
GAME_HELP_TEXT = "Clique em um nó ou ligação para começar. Depois escolha a relação evolutiva correspondente."

TREE_STYLESHEET_LEARNING = [
    {
        "selector": "node",
        "style": {
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
        },
    },
    {"selector": ".organism-node", "style": {"background-color": "#145c4c", "border-color": "#54f0c2"}},
    {
        "selector": ".internal-node",
        "style": {
            "background-color": "#6d385c",
            "border-color": "#c58aaf",
            "shape": "diamond",
            "width": 30,
            "height": 30,
            "font-size": "11px",
        },
    },
    {"selector": ".speciation-node", "style": {"background-color": "#147a65", "border-color": "#78f2c4", "border-width": 4}},
    {"selector": ".hybrid-node", "style": {"background-color": "#6d385c", "border-color": "#dba5ca", "border-width": 4}},
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "width": 3,
            "line-color": "#58756c",
            "target-arrow-color": "#58756c",
            "color": "#c5d2cb",
            "font-size": "10px",
            "label": "data(label)",
            "text-background-color": "#071311",
            "text-background-opacity": 0.88,
            "text-background-padding": "3px",
        },
    },
    {"selector": ".hybrid-edge", "style": {"line-color": "#b66b9a", "target-arrow-color": "#b66b9a", "target-arrow-shape": "triangle", "width": 4}},
    {"selector": ".transfer-edge", "style": {"line-color": "#e2687d", "target-arrow-color": "#e2687d", "target-arrow-shape": "triangle", "line-style": "dashed", "width": 4}},
]
TREE_STYLESHEET_GAME = [
    TREE_STYLESHEET_LEARNING[0],
    {"selector": ".organism-node", "style": {"background-color": "#173731", "border-color": "#7fb0a0"}},
    {
        "selector": ".internal-node",
        "style": {
            "background-color": "#324742",
            "border-color": "#93aca3",
            "shape": "diamond",
            "width": 30,
            "height": 30,
            "font-size": "11px",
        },
    },
    {"selector": ".speciation-node", "style": {"background-color": "#324742", "border-color": "#93aca3", "border-width": 2}},
    {"selector": ".hybrid-node", "style": {"background-color": "#324742", "border-color": "#93aca3", "border-width": 2}},
    {
        "selector": "edge",
        "style": {
            "curve-style": "bezier",
            "width": 3.5,
            "line-color": "#6d827c",
            "target-arrow-color": "#6d827c",
            "color": "#c5d2cb",
            "font-size": "10px",
            "label": "",
        },
    },
    {"selector": ".hybrid-edge", "style": {"line-color": "#91a39c", "target-arrow-color": "#91a39c", "target-arrow-shape": "triangle", "width": 4.5}},
    {"selector": ".transfer-edge", "style": {"line-color": "#91a39c", "target-arrow-color": "#91a39c", "target-arrow-shape": "triangle", "line-style": "dashed", "width": 4.5}},
]


def build_concept_card(index: int, slot: str) -> html.Article:
    title, description, icon = CONCEPTS[index]
    is_active = slot == "active"
    return html.Article(
        [
            html.Div(
                [
                    html.Div(icon, className="concept-icon", **{"aria-hidden": "true"}),
                    html.Span(f"{index + 1} de {len(CONCEPTS)}", className="concept-position"),
                ],
                className="concept-card-topline",
            ),
            html.H3(title),
            html.P(description),
        ],
        className="concept-carousel-card concept-card-active" if is_active else f"concept-carousel-card concept-card-preview {slot}",
        **{"aria-hidden": "false" if is_active else "true"},
    )


def build_concept_carousel(index: int) -> html.Div:
    previous_index = (index - 1) % len(CONCEPTS)
    next_index = (index + 1) % len(CONCEPTS)
    return html.Div(
        [html.Div([build_concept_card(previous_index, "left"), build_concept_card(index, "active"), build_concept_card(next_index, "right")], className="concept-carousel-track")],
        className="concept-carousel-content",
    )


def build_exercise_cards(examples: list[dict[str, Any]], selected_example_id: str) -> list[html.Button]:
    cards = []
    for index, example in enumerate(examples, start=1):
        class_name = "exercise-card is-active" if example["id"] == selected_example_id else "exercise-card"
        cards.append(
            html.Button(
                [
                    html.Div(
                        [
                            html.Span(f"Exercício {index}", className="eyebrow"),
                            html.Span(example["difficulty"], className=f"difficulty-badge difficulty-{example['difficulty'].lower()}"),
                        ],
                        className="card-topline",
                    ),
                    html.H3(example["title"]),
                    html.P(example["description"]),
                ],
                id={"type": "exercise-card", "index": example["id"]},
                n_clicks=0,
                className=class_name,
            )
        )
    return cards


def build_organism_table(organisms: list[dict[str, str]]) -> html.Div:
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th("Organismo"), html.Th("DNA"), html.Th("Descrição")])),
                html.Tbody([html.Tr([html.Td(item["name"]), html.Td(html.Code(item["sequence"])), html.Td(item["description"])]) for item in organisms]),
            ],
            className="organism-table",
        ),
        className="table-wrapper",
    )


def build_event_panel(expected_events: list[dict[str, Any]]) -> html.Div:
    events = describe_events(expected_events)
    if not events:
        return html.Div(
            [html.Span("Observação", className="event-icon neutral"), html.P("Este exemplo prioriza a comparação das sequências, sem evento especial.")],
            className="event-item",
        )
    return html.Div([html.Div([html.Span(event["label"], className=f"event-icon event-{event['event_type']}"), html.P(event["description"])], className="event-item") for event in events])


def build_interpretation(example: dict[str, Any], visible: bool) -> html.Div:
    return html.Div(
        [
            html.Div("Leitura guiada", className="eyebrow"),
            html.H3("O que esta árvore está contando?"),
            html.P(example["explanation"]),
            html.P("Dica: compare primeiro as sequências e depois siga os ramos até o ancestral compartilhado.", className="interpretation-tip"),
        ],
        className="interpretation-box" + ("" if visible else " is-hidden"),
    )


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


def build_results_summary(mode: str, example: dict[str, Any], solo_score: int, duel_state: dict[str, Any]) -> html.Div:
    if mode == "solo":
        heading = f"Pontuação final: {solo_score}"
    else:
        p1 = duel_state["player_1_score"]
        p2 = duel_state["player_2_score"]
        if p1 == p2:
            heading = f"Empate em {p1} ponto(s)"
        else:
            heading = f"Vencedor: Jogador {1 if p1 > p2 else 2}"
    return html.Div([html.H3(heading), html.P(example["explanation"]), build_event_panel(example["expected_events"])], className="interpretation-box")


def count_correct_events(submitted_answers: list[dict[str, Any]], total_events: int) -> int:
    if not submitted_answers:
        return 0
    event_ids = {answer["event_id"] for answer in submitted_answers if answer.get("correct") and answer.get("event_id")}
    return min(len(event_ids), total_events)


def count_duel_correct_events(duel_state: dict[str, Any]) -> int:
    return len({answer["event_id"] for answer in duel_state["answers"] if answer.get("correct") and answer.get("event_id")})


def build_mode_selector(active_mode: str) -> html.Div:
    return html.Div(
        [html.Button(label, id=f"mode-{mode_id}", n_clicks=0, className="mode-card is-active" if active_mode == mode_id else "mode-card") for mode_id, label in GAME_MODES.items()],
        className="mode-selector",
    )


def selected_element_text(selected_element: dict[str, Any] | None) -> tuple[str, str]:
    if not selected_element:
        return "Nenhum elemento selecionado ainda.", "Clique em um nó ou ligação na árvore."
    if selected_element["type"] == "edge":
        return "Você selecionou uma ligação evolutiva.", f"Origem: {selected_element['source']} · Destino: {selected_element['target']}"
    return f"Você selecionou: {selected_element['label']}", "Tipo: nó"


def build_tree_stylesheet(mode: str, reveal_results: bool, selected_element: dict[str, Any] | None) -> list[dict[str, Any]]:
    stylesheet = list(TREE_STYLESHEET_LEARNING if mode == "learning" or reveal_results else TREE_STYLESHEET_GAME)
    if selected_element:
        stylesheet.append(
            {
                "selector": f'node[id = "{selected_element["id"]}"], edge[id = "{selected_element["id"]}"]',
                "style": {
                    "border-color": "#54f0c2",
                    "border-width": 5,
                    "line-color": "#54f0c2",
                    "target-arrow-color": "#54f0c2",
                    "shadow-blur": 22,
                    "shadow-color": "#2ee6bd",
                    "shadow-opacity": 0.65,
                    "shadow-offset-x": 0,
                    "shadow-offset-y": 0,
                    "width": 5,
                },
            }
        )
    return stylesheet


def get_tree_payload(example_id: str, mode: str, reveal_results: bool, selected_element: dict[str, Any] | None) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], html.Div]:
    example = get_example_by_id(EXAMPLES, example_id)
    graph = build_example_graph(example)
    interpretation_visible = mode == "learning" or reveal_results
    stylesheet = build_tree_stylesheet(mode, reveal_results, selected_element)
    return example, build_cytoscape_elements(graph), stylesheet, build_interpretation(example, interpretation_visible)


EXAMPLES = load_examples()
FIRST_EXAMPLE = EXAMPLES[0]

app = Dash(__name__, title="EvoRamos", update_title="Carregando...")
server = app.server

app.layout = html.Main(
    [
        dcc.Store(id="concept-index", data=0),
        dcc.Store(id="selected-example-id", data=FIRST_EXAMPLE["id"]),
        dcc.Store(id="selected-tree-element", data=None),
        dcc.Store(id="selected-answer-choice", data=None),
        dcc.Store(id="submitted-answers", data=[]),
        dcc.Store(id="solo-score", data=0),
        dcc.Store(id="duel-state", data=EMPTY_DUEL_STATE.copy()),
        dcc.Store(id="game-mode", data="learning"),
        dcc.Store(id="answer-feedback", data=None),
        dcc.Store(id="reveal-results", data=False),
        dcc.Store(id="tree-zoom", data=1.0),
        dcc.Store(id="tree-layout-seed", data=0),
        html.Header(
            [
                html.Div([html.Span("BIOLOGIA + TECNOLOGIA", className="hero-kicker"), html.H1(["Evo", html.Span("Ramos")]), html.H2("Interprete árvores filogenéticas em modo aula, desafio e duelo."), html.P("Compare sequências fictícias de DNA, explore relações evolutivas e descubra como diferentes eventos aparecem em uma árvore."), html.A("Começar pelos exercícios", href="#exercicios", className="hero-button")], className="hero-content"),
                html.Div([html.Div("A", className="dna-base base-a"), html.Div("T", className="dna-base base-t"), html.Div("C", className="dna-base base-c"), html.Div("G", className="dna-base base-g")], className="hero-visual"),
            ],
            className="hero",
        ),
        html.Section(
            [
                html.Div([html.Span("BASES PARA EXPLORAR", className="eyebrow"), html.H2(["Conceitos ", html.Span("biológicos"), " essenciais"]), html.P("Explore os principais conceitos antes de interpretar os ramos.")], className="section-heading"),
                html.Div([html.Button("Anterior", id="previous-concept", n_clicks=0, className="carousel-button"), html.Div(build_concept_carousel(0), id="concept-carousel-card", className="concept-carousel-stage"), html.Button("Próximo", id="next-concept", n_clicks=0, className="carousel-button")], className="concept-carousel"),
            ],
            className="content-section concept-carousel-section",
        ),
        html.Section(
            [
                html.Div([html.Span("PRÁTICA GUIADA", className="eyebrow"), html.H2("Exercícios prontos"), html.P("Escolha um cenário e mude entre aprendizado, desafio e duelo local.")], className="section-heading"),
                html.Div(build_mode_selector("learning"), id="mode-selector-wrapper"),
                html.Div(build_exercise_cards(EXAMPLES, FIRST_EXAMPLE["id"]), id="exercise-card-grid", className="exercise-grid"),
            ],
            className="content-section",
            id="exercicios",
        ),
        html.Section(
            [
                html.Div(id="example-heading-shell", className="example-main"),
                html.Div(id="game-status-bar", className="game-status-bar"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div([html.Span("VISUALIZAÇÃO", className="eyebrow"), html.H2("Árvore do exemplo")]),
                                        html.Div(
                                            [
                                                html.Button("Zoom +", id="tree-zoom-in", n_clicks=0, className="tree-control-button"),
                                                html.Button("Zoom -", id="tree-zoom-out", n_clicks=0, className="tree-control-button"),
                                                html.Button("Recentralizar", id="tree-reset-view", n_clicks=0, className="tree-control-button"),
                                                html.Button("Mostrar interpretação do exemplo", id="show-interpretation", n_clicks=0, className="action-button"),
                                            ],
                                            className="tree-toolbar-actions",
                                        ),
                                    ],
                                    className="tree-toolbar",
                                ),
                                html.Div(id="legend-wrapper"),
                                cyto.Cytoscape(
                                    id="phylogenetic-tree",
                                    elements=[],
                                    layout=DEFAULT_TREE_LAYOUT,
                                    zoom=1.0,
                                    minZoom=0.45,
                                    maxZoom=2.2,
                                    stylesheet=TREE_STYLESHEET_LEARNING,
                                    responsive=True,
                                    className="tree-canvas",
                                ),
                                html.Div(id="interpretation-panel"),
                            ],
                            id="tree-column",
                            className="game-tree-column",
                        ),
                        html.Aside(
                            [
                                html.Div([html.Span("SUA JOGADA", className="eyebrow"), html.H3("Sua jogada"), html.P("Siga os passos para interpretar a árvore.", className="sidebar-subtitle")]),
                                html.Div(
                                    [
                                        html.Div([html.Span("Passo 1", className="step-label"), html.P("Clique em um nó ou ligação na árvore.")], className="step-card"),
                                        html.Div([html.P(id="selected-element-label"), html.Small(id="selected-element-type")], className="selected-element-card"),
                                        html.Button("Limpar seleção", id="clear-selection", n_clicks=0, className="secondary-action-button"),
                                        html.Div([html.Span("Passo 2", className="step-label"), html.P("Escolha a relação evolutiva.")], className="step-card"),
                                        html.Div(
                                            [
                                                html.Button(option["label"], id={"type": "answer-choice", "value": option["value"]}, n_clicks=0, className="answer-choice")
                                                for option in ANSWER_OPTIONS
                                            ],
                                            id="answer-choice-grid",
                                            className="answer-choice-grid",
                                        ),
                                        html.Div([html.Span("Passo 3", className="step-label"), html.P("Confirme a jogada para validar sua interpretação.")], className="step-card"),
                                        html.Button("Confirmar resposta", id="submit-answer", n_clicks=0, className="primary-game-button"),
                                        html.Button("Finalizar desafio", id="finish-challenge", n_clicks=0, className="finish-challenge-button"),
                                        html.Button("Reiniciar desafio", id="reset-game", n_clicks=0, className="reset-game-button"),
                                        html.Div(id="answer-feedback-box", className="feedback-box"),
                                        html.Div(id="answer-help-box", className="help-box"),
                                        html.Div(id="results-summary"),
                                    ],
                                    id="answer-panel",
                                    className="answer-panel",
                                ),
                            ],
                            id="game-sidebar",
                            className="game-sidebar",
                        ),
                    ],
                    id="main-game-layout",
                    className="game-layout",
                ),
                html.Div(
                    [
                        html.Div(id="learning-goal", className="info-box"),
                        html.Div(
                            [
                                html.Details([html.Summary("Ver organismos e sequências"), html.Div(id="organism-table")], className="accordion-section"),
                                html.Details([html.Summary("Ver objetivo de aprendizagem"), html.Div(id="secondary-goal-copy")], className="accordion-section"),
                                html.Details([html.Summary("Ver descrição do exemplo"), html.Div(id="secondary-description")], className="accordion-section"),
                                html.Details([html.Summary("Ver explicação final"), html.Div(id="secondary-explanation")], className="accordion-section"),
                            ],
                            className="secondary-content-tabs",
                        ),
                    ],
                    id="secondary-content",
                ),
            ],
            className="example-shell",
        ),
    ],
    className="page",
)


@app.callback(Output("concept-index", "data"), Input("previous-concept", "n_clicks"), Input("next-concept", "n_clicks"), State("concept-index", "data"), prevent_initial_call=True)
def update_concept_index(_previous_clicks: int, _next_clicks: int, current_index: int) -> int:
    direction = -1 if ctx.triggered_id == "previous-concept" else 1
    return (current_index + direction) % len(CONCEPTS)


@app.callback(Output("concept-carousel-card", "children"), Input("concept-index", "data"))
def render_concept_card(index: int) -> html.Div:
    return build_concept_carousel(index)


@app.callback(Output("game-mode", "data"), Input("mode-learning", "n_clicks"), Input("mode-solo", "n_clicks"), Input("mode-duel", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
def update_game_mode(_learning: int, _solo: int, _duel: int, current_mode: str) -> str:
    if not ctx.triggered_id:
        return current_mode
    return ctx.triggered_id.replace("mode-", "")


@app.callback(
    Output("mode-learning", "className"),
    Output("mode-solo", "className"),
    Output("mode-duel", "className"),
    Input("game-mode", "data"),
)
def update_mode_button_classes(active_mode: str) -> tuple[str, str, str]:
    """Atualiza apenas as classes dos botões de modo, sem recriar o layout.

    Recriar `mode-selector-wrapper.children` gerava risco de dependência circular,
    porque os próprios botões recriados também eram Inputs da callback que altera
    `game-mode`.
    """
    return tuple(
        "mode-card is-active" if mode_id == active_mode else "mode-card"
        for mode_id in GAME_MODES
    )


@app.callback(Output("selected-example-id", "data"), Input({"type": "exercise-card", "index": ALL}, "n_clicks"), State("selected-example-id", "data"), prevent_initial_call=True)
def select_example_from_card(_clicks: list[int], current_example_id: str) -> str:
    triggered = ctx.triggered_id
    if not triggered:
        return current_example_id
    return triggered["index"]


@app.callback(Output({"type": "exercise-card", "index": ALL}, "className"), Input("selected-example-id", "data"))
def update_active_exercise_card(selected_example_id: str) -> list[str]:
    return ["exercise-card is-active" if example["id"] == selected_example_id else "exercise-card" for example in EXAMPLES]


@app.callback(Output("selected-answer-choice", "data"), Input({"type": "answer-choice", "value": ALL}, "n_clicks"), State("selected-answer-choice", "data"), prevent_initial_call=True)
def select_answer_choice(_clicks: list[int], current_choice: str | None) -> str | None:
    triggered = ctx.triggered_id
    if not triggered:
        return current_choice
    return triggered["value"]


@app.callback(Output({"type": "answer-choice", "value": ALL}, "className"), Input("selected-answer-choice", "data"))
def update_answer_choice_classes(selected_choice: str | None) -> list[str]:
    classes = []
    for option in ANSWER_OPTIONS:
        class_name = "answer-choice"
        if option["value"] == selected_choice:
            class_name += " is-selected"
        classes.append(class_name)
    return classes


@app.callback(
    Output("selected-tree-element", "data"),
    Input("phylogenetic-tree", "tapNodeData"),
    Input("phylogenetic-tree", "tapEdgeData"),
    prevent_initial_call=True,
)
def update_selected_tree_element(node_data: dict[str, Any] | None, edge_data: dict[str, Any] | None) -> dict[str, Any] | None:
    """Salva o nó ou aresta clicado no Cytoscape.

    `tapNodeData` e `tapEdgeData` pertencem ao mesmo componente. Por isso,
    `ctx.triggered_id` sozinho não informa qual propriedade mudou. Usamos
    `prop_id` para não reaproveitar uma aresta antiga quando o jogador clicar
    em um nó depois de ter clicado em uma aresta.
    """
    if not ctx.triggered:
        return no_update

    triggered_prop = ctx.triggered[0]["prop_id"].split(".")[-1]

    if triggered_prop == "tapEdgeData" and edge_data:
        return {
            "id": edge_data["id"],
            "label": edge_data.get("label") or "Ligação evolutiva",
            "type": "edge",
            "source": edge_data["source"],
            "target": edge_data["target"],
        }

    if triggered_prop == "tapNodeData" and node_data:
        return {"id": node_data["id"], "label": node_data.get("label", node_data["id"]), "type": "node"}

    return no_update


@app.callback(
    Output("selected-tree-element", "data", allow_duplicate=True),
    Output("selected-answer-choice", "data", allow_duplicate=True),
    Input("clear-selection", "n_clicks"),
    prevent_initial_call=True,
)
def clear_selected_element(_clicks: int) -> tuple[None, None]:
    return None, None


@app.callback(
    Output("tree-zoom", "data"),
    Output("tree-layout-seed", "data"),
    Input("tree-zoom-in", "n_clicks"),
    Input("tree-zoom-out", "n_clicks"),
    Input("tree-reset-view", "n_clicks"),
    State("tree-zoom", "data"),
    State("tree-layout-seed", "data"),
    prevent_initial_call=True,
)
def update_tree_controls(_zoom_in: int, _zoom_out: int, _reset_view: int, current_zoom: float, current_seed: int) -> tuple[float, int]:
    triggered = ctx.triggered_id
    if triggered == "tree-zoom-in":
        return min(round(current_zoom + 0.15, 2), 2.2), current_seed
    if triggered == "tree-zoom-out":
        return max(round(current_zoom - 0.15, 2), 0.45), current_seed
    return 1.0, current_seed + 1


@app.callback(
    Output("selected-tree-element", "data", allow_duplicate=True),
    Output("selected-answer-choice", "data", allow_duplicate=True),
    Output("submitted-answers", "data"),
    Output("solo-score", "data"),
    Output("duel-state", "data"),
    Output("answer-feedback", "data"),
    Output("reveal-results", "data"),
    Output("tree-zoom", "data", allow_duplicate=True),
    Input("selected-example-id", "data"),
    Input("game-mode", "data"),
    Input("reset-game", "n_clicks"),
    prevent_initial_call=True,
)
def reset_game_state(_example_id: str, _game_mode: str, _reset_clicks: int) -> tuple[None, None, list[dict[str, Any]], int, dict[str, Any], None, bool, float]:
    return None, None, [], 0, EMPTY_DUEL_STATE.copy(), None, False, 1.0


@app.callback(
    Output("submitted-answers", "data", allow_duplicate=True),
    Output("solo-score", "data", allow_duplicate=True),
    Output("duel-state", "data", allow_duplicate=True),
    Output("answer-feedback", "data", allow_duplicate=True),
    Output("selected-answer-choice", "data", allow_duplicate=True),
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
def submit_player_answer(
    _clicks: int,
    example_id: str,
    game_mode: str,
    selected_element: dict[str, Any] | None,
    selected_event_type: str | None,
    submitted_answers: list[dict[str, Any]],
    solo_score: int,
    duel_state: dict[str, Any],
):
    example = get_example_by_id(EXAMPLES, example_id)
    player_id = duel_state["current_player"] if game_mode == "duel" else None
    score_history = duel_state["answers"] if game_mode == "duel" else submitted_answers
    result = check_player_answer(example, selected_element, selected_event_type, score_history, player_id=player_id)
    answer_record = result.pop("answer_record")

    if game_mode == "duel":
        prefix = f"Jogador {duel_state['current_player']}"
        if result["correct"]:
            result["message"] = f"{prefix} acertou: +{result['points']} ponto. Agora é a vez do Jogador {2 if duel_state['current_player'] == 1 else 1}."
        elif selected_element and selected_event_type:
            result["message"] = f"{prefix} errou. Agora é a vez do Jogador {2 if duel_state['current_player'] == 1 else 1}."

    if not answer_record:
        return submitted_answers, solo_score, duel_state, result, selected_event_type

    if game_mode == "solo":
        updated_answers = submitted_answers + [answer_record]
        return updated_answers, solo_score + result["points"], duel_state, result, None

    updated_duel_state = {
        **duel_state,
        "answers": duel_state["answers"] + [answer_record],
        "current_player": 2 if duel_state["current_player"] == 1 else 1,
    }
    if result["points"]:
        score_key = "player_1_score" if player_id == 1 else "player_2_score"
        updated_duel_state[score_key] = duel_state[score_key] + result["points"]
    return submitted_answers, solo_score, updated_duel_state, result, None


@app.callback(Output("reveal-results", "data", allow_duplicate=True), Input("show-interpretation", "n_clicks"), Input("finish-challenge", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
def update_reveal_results(_show_clicks: int, _finish_clicks: int, game_mode: str) -> bool:
    if ctx.triggered_id == "show-interpretation":
        return True
    return game_mode in {"solo", "duel"}


@app.callback(
    Output("example-heading-shell", "children"),
    Output("game-status-bar", "children"),
    Output("game-status-bar", "style"),
    Output("tree-column", "className"),
    Output("game-sidebar", "className"),
    Output("main-game-layout", "className"),
    Output("learning-goal", "children"),
    Output("secondary-goal-copy", "children"),
    Output("secondary-description", "children"),
    Output("secondary-explanation", "children"),
    Output("organism-table", "children"),
    Output("selected-element-label", "children"),
    Output("selected-element-type", "children"),
    Output("finish-challenge", "children"),
    Output("reset-game", "children"),
    Output("reset-game", "style"),
    Output("show-interpretation", "style"),
    Output("answer-feedback-box", "children"),
    Output("answer-feedback-box", "className"),
    Output("answer-help-box", "children"),
    Output("results-summary", "children"),
    Output("legend-wrapper", "children"),
    Output("phylogenetic-tree", "elements"),
    Output("phylogenetic-tree", "stylesheet"),
    Output("phylogenetic-tree", "zoom"),
    Output("phylogenetic-tree", "layout"),
    Output("interpretation-panel", "children"),
    Output("secondary-content", "className"),
    Input("selected-example-id", "data"),
    Input("game-mode", "data"),
    Input("selected-tree-element", "data"),
    Input("selected-answer-choice", "data"),
    Input("submitted-answers", "data"),
    Input("solo-score", "data"),
    Input("duel-state", "data"),
    Input("answer-feedback", "data"),
    Input("reveal-results", "data"),
    Input("tree-zoom", "data"),
    Input("tree-layout-seed", "data"),
)
def render_example(
    example_id: str,
    game_mode: str,
    selected_tree_element: dict[str, Any] | None,
    selected_answer_choice: str | None,
    submitted_answers: list[dict[str, Any]],
    solo_score: int,
    duel_state: dict[str, Any],
    answer_feedback: dict[str, Any] | None,
    reveal_results: bool,
    tree_zoom: float,
    tree_layout_seed: int,
):
    example, elements, stylesheet, interpretation = get_tree_payload(example_id, game_mode, reveal_results, selected_tree_element)
    found_events = count_correct_events(submitted_answers, len(example["expected_events"]))
    duel_found_events = count_duel_correct_events(duel_state)

    heading = [
        html.Div([html.Span(example["difficulty"], className=f"difficulty-badge difficulty-{example['difficulty'].lower()}"), html.Span(example["tree_mode"].replace("_", " "), className="mode-label")], className="example-meta"),
        html.H2(example["title"]),
        html.P(example["description"], className="example-description"),
    ]
    learning_goal = [html.Strong("Objetivo de aprendizagem"), html.P(example["learning_goal"])]
    selected_label, selected_type = selected_element_text(selected_tree_element)
    feedback_text = "Clique em um nó ou ligação para começar."
    feedback_class = "feedback-box"
    if answer_feedback:
        feedback_text = answer_feedback.get("message", feedback_text)
        feedback_class += " correct" if answer_feedback.get("correct") else " incorrect"

    help_text = GAME_HELP_TEXT
    if not selected_tree_element:
        help_text = "Passo 1: selecione um elemento na árvore. Passo 2: escolha uma relação evolutiva."
    elif not selected_answer_choice:
        help_text = "Selecione uma opção de resposta antes de confirmar."
    else:
        help_text = "Tudo pronto. Confirme a jogada para validar sua interpretação."

    status_bar_style = {"display": "none"}
    status_bar_children = []
    reset_label = "Reiniciar desafio"
    finish_label = "Finalizar desafio"
    reset_style = {"display": "none"}
    show_interpretation_style = {} if game_mode == "learning" else {"display": "none"}
    secondary_content_class = "secondary-content-stack"
    tree_column_class = "game-tree-column"
    sidebar_class = "game-sidebar"
    layout_class = "game-layout"

    if game_mode == "solo":
        status_bar_style = {}
        status_bar_children = [
            html.Span("Desafio individual", className="mode-badge"),
            html.Span(f"Pontuação: {solo_score}", className="score-pill"),
            html.Span(f"Eventos encontrados: {found_events} / {len(example['expected_events'])}", className="score-pill"),
            html.Button("Reiniciar desafio", id="status-reset-button-proxy", className="status-button status-button-muted", disabled=True),
        ]
        reset_style = {}
        secondary_content_class += " is-game-mode"
    elif game_mode == "duel":
        status_bar_style = {}
        status_bar_children = [
            html.Span("Duelo local", className="mode-badge"),
            html.Span(f"Jogador 1: {duel_state['player_1_score']}", className="score-pill"),
            html.Span(f"Jogador 2: {duel_state['player_2_score']}", className="score-pill"),
            html.Span(f"Vez do Jogador {duel_state['current_player']}", className="turn-indicator"),
            html.Span(f"Progresso: {duel_found_events} / {len(example['expected_events'])}", className="score-pill"),
        ]
        reset_label = "Reiniciar duelo"
        finish_label = "Encerrar duelo"
        reset_style = {}
        secondary_content_class += " is-game-mode"

    if game_mode == "learning":
        layout_class += " is-learning"
        tree_column_class += " is-learning"
        sidebar_class += " is-learning"
    else:
        layout_class += " is-game-mode"
        tree_column_class += " is-game-mode"
        sidebar_class += " is-game-mode"

    summary = build_results_summary(game_mode, example, solo_score, duel_state) if game_mode != "learning" and reveal_results else None
    layout = {**DEFAULT_TREE_LAYOUT, "spacingFactor": 1.55, "padding": 45 + tree_layout_seed * 0}

    return (
        heading,
        status_bar_children,
        status_bar_style,
        tree_column_class,
        sidebar_class,
        layout_class,
        learning_goal,
        learning_goal,
        html.P(example["description"]),
        html.P(example["explanation"] if reveal_results or game_mode == "learning" else "Finalize o modo atual para revelar a explicação completa."),
        build_organism_table(example["organisms"]),
        selected_label,
        selected_type,
        finish_label,
        reset_label,
        reset_style,
        show_interpretation_style,
        feedback_text,
        feedback_class,
        help_text,
        summary,
        build_legend(game_mode if not reveal_results else "learning"),
        elements,
        stylesheet,
        tree_zoom,
        layout,
        interpretation,
        secondary_content_class,
    )


if __name__ == "__main__":
    app.run(debug=True)
