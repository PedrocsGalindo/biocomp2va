"""Componentes e estilos da árvore Cytoscape."""

from __future__ import annotations

from typing import Any

import dash_cytoscape as cyto
from dash import html

from frontend.state import DEFAULT_TREE_LAYOUT
from src.cytoscape_elements import build_cytoscape_elements
from src.free_classification import apply_user_annotations, endpoint_id
from src.tree_builder import build_example_graph, build_phylogenetic_tree

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

USER_ANNOTATION_STYLES = [
    {"selector": ".user-annotated-node", "style": {"label": "data(display_label)", "text-background-color": "#071311", "text-background-opacity": 0.88, "text-background-padding": "3px", "border-width": 5}},
    {"selector": "node.user-speciation", "style": {"background-color": "#147a65", "border-color": "#78f2c4", "shadow-blur": 18, "shadow-color": "#54f0c2", "shadow-opacity": 0.35}},
    {"selector": "node.user-common-ancestor", "style": {"background-color": "#1f4d5a", "border-color": "#7bd2f4", "shadow-blur": 18, "shadow-color": "#59bdf7", "shadow-opacity": 0.35}},
    {"selector": "node.user-unclassified", "style": {"background-color": "#4a5551", "border-color": "#a7b8b1"}},
    {"selector": "node.user-hybridization", "style": {"background-color": "#6d385c", "border-color": "#dba5ca", "shadow-blur": 18, "shadow-color": "#c58aaf", "shadow-opacity": 0.35}},
    {"selector": "node.user-horizontal-transfer", "style": {"background-color": "#5b3c1b", "border-color": "#f6b44b", "shadow-blur": 18, "shadow-color": "#f6b44b", "shadow-opacity": 0.35}},
    {"selector": ".user-annotated-edge", "style": {"label": "data(relation_label)", "color": "#f3efe4", "font-size": "10px", "font-weight": "700", "text-background-color": "#071311", "text-background-opacity": 0.88, "text-background-padding": "3px", "text-rotation": "autorotate", "width": 5}},
    {"selector": "edge.user-speciation", "style": {"line-color": "#78f2c4", "target-arrow-color": "#78f2c4"}},
    {"selector": "edge.user-common-ancestor", "style": {"line-color": "#7bd2f4", "target-arrow-color": "#7bd2f4"}},
    {"selector": "edge.user-unclassified", "style": {"line-color": "#a7b8b1", "target-arrow-color": "#a7b8b1"}},
    {"selector": "edge.user-horizontal-transfer", "style": {"curve-style": "bezier", "line-style": "dashed", "line-color": "#f6b44b", "target-arrow-color": "#f6b44b", "target-arrow-shape": "triangle", "width": 5, "label": "data(relation_label)", "z-index": 980}},
    {"selector": "edge.user-hybridization", "style": {"curve-style": "bezier", "line-style": "solid", "line-color": "#c58aaf", "target-arrow-color": "#c58aaf", "target-arrow-shape": "triangle", "width": 5, "label": "data(relation_label)", "z-index": 980}},
]


def build_tree_stylesheet(mode: str, reveal: bool, selected: dict[str, Any] | None, highlight: dict[str, list[str]] | None, draft: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    stylesheet = list(TREE_STYLESHEET_LEARNING if mode == "learning" or reveal else TREE_STYLESHEET_GAME)
    if mode == "free":
        stylesheet.extend(USER_ANNOTATION_STYLES)
    if selected:
        element_id = selected.get("id")
        if selected.get("type") == "node":
            stylesheet.append({"selector": f'node[id = "{element_id}"]', "style": {"border-color": "#54f0c2", "border-width": 5, "shadow-blur": 22, "shadow-color": "#2ee6bd", "shadow-opacity": 0.65, "shadow-offset-x": 0, "shadow-offset-y": 0}})
        else:
            stylesheet.append({"selector": f'edge[id = "{element_id}"]', "style": {"line-color": "#54f0c2", "target-arrow-color": "#54f0c2", "width": 6, "shadow-blur": 22, "shadow-color": "#2ee6bd", "shadow-opacity": 0.65}})
    if mode == "free" and draft:
        source_id = endpoint_id(draft.get("source"))
        target_id = endpoint_id(draft.get("target"))
        if source_id:
            stylesheet.append({"selector": f'node[id = "{source_id}"]', "style": {"border-color": "#f6b44b", "border-width": 6, "shadow-blur": 26, "shadow-color": "#f6b44b", "shadow-opacity": 0.72}})
        if target_id:
            stylesheet.append({"selector": f'node[id = "{target_id}"]', "style": {"border-color": "#c58aaf", "border-width": 6, "shadow-blur": 26, "shadow-color": "#c58aaf", "shadow-opacity": 0.72}})
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


def tree_payload(
    example: dict[str, Any],
    mode: str,
    reveal: bool,
    selected: dict[str, Any] | None,
    highlight: dict[str, list[str]] | None,
    annotations: list[dict[str, Any]] | None = None,
    draft: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    graph = build_phylogenetic_tree(example["organisms"]) if mode == "free" else build_example_graph(example)
    elements = build_cytoscape_elements(graph)
    if mode == "free":
        elements = apply_user_annotations(elements, annotations or [])
    return elements, build_tree_stylesheet(mode, reveal, selected, highlight, draft)


def build_tree_column(game_panel: Any | None = None, free_panel: Any | None = None) -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    html.Button("+", id="tree-zoom-in", n_clicks=0, className="tree-small-action", title="Ampliar"),
                    html.Button("−", id="tree-zoom-out", n_clicks=0, className="tree-small-action", title="Reduzir"),
                    html.Button("⦿", id="tree-reset-view", n_clicks=0, className="tree-small-action", title="Recentralizar"),
                ],
                className="tree-actions-toolbar tree-zoom-toolbar",
            ),
            html.Div(id="legend-wrapper"),
            html.Div(id="interpretation-panel"),
            game_panel if game_panel is not None else html.Div(),
            free_panel if free_panel is not None else html.Div(),
            html.Div(
                [
                    html.Div(
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
                        className="tree-canvas-shell",
                    ),
                    html.Aside(
                        html.Div(id="organism-table", className="tree-organisms-panel"),
                        className="tree-side-panel",
                    ),
                ],
                className="tree-stage-grid",
            ),
            html.Div(
                [
                    html.Button(
                        [html.Span("↓", className="download-icon", **{"aria-hidden": "true"}), html.Span("Baixar árvore")],
                        id="download-annotated-tree",
                        n_clicks=0,
                        className="tree-small-action download-tree-button is-hidden",
                        title="Baixar árvore anotada",
                    ),
                    html.Button("Limpar", id="clear-free-annotations", n_clicks=0, className="tree-small-action clear-tree-button is-hidden", title="Limpar anotações"),
                    html.Button("🗑", id="delete-selected-relation", n_clicks=0, className="tree-small-action danger-icon-button is-hidden", title="Excluir relação especial selecionada"),
                ],
                className="tree-actions-toolbar tree-annotation-toolbar",
            ),
        ],
        id="tree-column",
        className="game-tree-column",
    )


def build_legend(mode: str) -> html.Div:
    if mode == "learning":
        items = [
            html.Span([html.I(className="legend-dot organism"), "Organismo"]),
            html.Span([html.I(className="legend-dot ancestor"), "Ancestral"]),
            html.Span([html.I(className="legend-line hybrid"), "Hibridização"]),
            html.Span([html.I(className="legend-line transfer"), "Transferência horizontal"]),
        ]
    elif mode == "free":
        items = [
            html.Span([html.I(className="legend-dot organism neutral"), "Organismo"]),
            html.Span([html.I(className="legend-dot ancestor neutral"), "Ancestral"]),
            html.Span([html.I(className="legend-line annotated"), "Classificação aplicada"]),
            html.Span([html.I(className="legend-line transfer-user"), "Transferência horizontal"]),
            html.Span([html.I(className="legend-line hybrid-user"), "Contribuição híbrida"]),
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
        "free": "Use a barra de classificação. Para relação especial: escolha o tipo, clique na origem e depois no destino.",
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
    elif mode == "free":
        title = "Classificação livre"
        text = "Neste modo, o sistema monta a árvore por similaridade. Relações especiais são criadas manualmente pelo usuário."
        tip = "Não há gabarito, pontuação ou correção automática: a anotação representa a sua interpretação."
    else:
        title = "Dica"
        text = "Observe se você clicou em um nó interno, em uma ligação comum ou em uma ligação especial entre ramos."
        tip = "A dica ajuda a classificar o elemento, mas não revela o gabarito."
    return html.Div(
        [html.Div(title, className="eyebrow"), html.H3(title), html.P(text), html.P(tip, className="interpretation-tip")],
        className="guided-reading-box" + ("" if visible else " is-hidden"),
    )


def build_organism_table(example: dict[str, Any]) -> html.Div:
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th("Organismo"), html.Th("DNA"), html.Th("Descrição")])),
                html.Tbody(
                    [
                        html.Tr([html.Td(org["name"]), html.Td(html.Code(org["sequence"])), html.Td(org["description"])])
                        for org in example["organisms"]
                    ]
                ),
            ],
            className="organism-table",
        ),
        className="table-wrapper",
    )
