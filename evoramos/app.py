"""Aplicação web mínima do jogo educativo EvoRamos."""

import json
from pathlib import Path

import dash_cytoscape as cyto
from dash import Dash, Input, Output, html

from src.cytoscape_elements import build_cytoscape_elements
from src.tree_builder import build_phylogenetic_tree


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sequences.json"


def load_sequences() -> list[dict]:
    """Carrega os organismos fictícios usados pelo MVP."""
    with DATA_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def build_organism_table(sequences: list[dict]) -> html.Table:
    """Cria uma tabela HTML simples com os organismos e suas sequências."""
    return html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Organismo"),
                        html.Th("Sequência de DNA"),
                        html.Th("Descrição"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(organism["name"]),
                            html.Td(html.Code(organism["sequence"])),
                            html.Td(organism["description"]),
                        ]
                    )
                    for organism in sequences
                ]
            ),
        ],
        className="organism-table",
    )


sequences = load_sequences()
initial_graph = build_phylogenetic_tree(sequences)

app = Dash(__name__, title="EvoRamos")
server = app.server

app.layout = html.Main(
    [
        html.Header(
            [
                html.H1("EvoRamos"),
                html.P(
                    "Um jogo educativo para explorar árvores filogenéticas "
                    "e reconhecer eventos da evolução."
                ),
            ],
            className="hero",
        ),
        html.Section(
            [
                html.H2("Organismos fictícios"),
                build_organism_table(sequences),
            ],
            className="panel",
        ),
        html.Section(
            [
                html.H2("Árvore filogenética inicial"),
                html.Button(
                    "Gerar árvore filogenética",
                    id="generate-tree-button",
                    n_clicks=0,
                    className="action-button",
                ),
                cyto.Cytoscape(
                    id="phylogenetic-tree",
                    elements=build_cytoscape_elements(initial_graph),
                    layout={"name": "breadthfirst", "directed": False},
                    style={"width": "100%", "height": "430px"},
                    stylesheet=[
                        {
                            "selector": "node",
                            "style": {
                                "label": "data(label)",
                                "background-color": "#4f7f68",
                                "color": "#20312b",
                                "font-size": "12px",
                                "text-valign": "bottom",
                                "text-margin-y": "8px",
                            },
                        },
                        {
                            "selector": "edge",
                            "style": {
                                "label": "data(label)",
                                "line-color": "#9bb2a5",
                                "width": 3,
                                "font-size": "10px",
                                "text-background-color": "#ffffff",
                                "text-background-opacity": 1,
                            },
                        },
                    ],
                ),
            ],
            className="panel",
        ),
    ],
    className="page",
)


@app.callback(
    Output("phylogenetic-tree", "elements"),
    Input("generate-tree-button", "n_clicks"),
)
def generate_tree(_n_clicks: int) -> list[dict]:
    """Reconstrói o grafo de exemplo quando o jogador usa o botão."""
    graph = build_phylogenetic_tree(sequences)
    return build_cytoscape_elements(graph)


if __name__ == "__main__":
    app.run(debug=True)
