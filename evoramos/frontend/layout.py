"""Layout principal do app Dash."""

from __future__ import annotations

from copy import deepcopy

from dash import dcc, html

from frontend.components.concepts import build_concept_carousel
from frontend.components.exercises import build_exercise_cards, build_mode_selector
from frontend.components.free_classification_panel import build_free_classification_panel
from frontend.components.game_sidebar import build_game_answer_panel, build_game_sidebar
from frontend.components.hero import build_hero
from frontend.components.import_sequences import build_sequence_upload
from frontend.components.tree_view import build_instructions_strip, build_tree_column
from frontend.state import EMPTY_CUSTOM_RELATION_DRAFT, EMPTY_DUEL_STATE, FIRST_EXAMPLE


def create_layout() -> html.Main:
    return html.Main(
        [
            dcc.Store(id="concept-index", data=0),
            dcc.Store(id="selected-example-id", data=FIRST_EXAMPLE["id"]),
            dcc.Store(id="imported-example", data=None),
            dcc.Store(id="game-mode", data="learning"),
            dcc.Store(id="selected-tree-element", data=None),
            dcc.Store(id="selected-answer-choice", data=None),
            dcc.Store(id="selected-free-classification", data=None),
            dcc.Store(id="free-action-mode", data="classify"),
            dcc.Store(id="custom-relation-draft", data=deepcopy(EMPTY_CUSTOM_RELATION_DRAFT)),
            dcc.Store(id="user-annotations", data=[]),
            dcc.Store(id="free-feedback", data=None),
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
            build_hero(),
            html.Section(
                [
                    html.Div(
                        [
                            html.Span("BASES PARA EXPLORAR", className="eyebrow"),
                            html.H2(["Conceitos ", html.Span("biológicos"), " essenciais"]),
                            html.P("Explore os principais conceitos antes de interpretar os ramos."),
                        ],
                        className="section-heading",
                    ),
                    html.Div(
                        [
                            html.Button("Anterior", id="previous-concept", n_clicks=0, className="carousel-button"),
                            html.Div(build_concept_carousel(0), id="concept-carousel-card", className="concept-carousel-stage"),
                            html.Button("Próximo", id="next-concept", n_clicks=0, className="carousel-button"),
                        ],
                        className="concept-carousel",
                    ),
                ],
                className="content-section concept-carousel-section",
            ),
            html.Section(
                [
                    html.Div(
                        [
                            html.Span("PRÁTICA GUIADA", className="eyebrow"),
                            html.H2("Exercícios prontos"),
                            html.P("Escolha um cenário, importe sequências em TXT ou mude entre aprendizado, desafio, duelo e classificação livre."),
                        ],
                        className="section-heading",
                    ),
                    html.Div(build_mode_selector("learning"), id="mode-selector-wrapper"),
                    build_sequence_upload(),
                    html.Div(id="sequence-upload-status", className="upload-status"),
                    html.Div(build_exercise_cards(FIRST_EXAMPLE["id"]), id="exercise-card-grid", className="exercise-grid"),
                ],
                className="content-section",
                id="exercicios",
            ),
            html.Section(
                [
                    html.Div(id="game-status-bar", className="game-status-bar"),
                    html.Div(build_instructions_strip("learning", False), id="game-instructions-shell"),
                    html.Div(
                        [
                            build_tree_column(game_panel=build_game_answer_panel(), free_panel=build_free_classification_panel()),
                            build_game_sidebar(),
                            html.Div(id="results-summary", className="game-correction-section"),
                        ],
                        id="main-game-layout",
                        className="game-layout",
                    ),
                    # Mantém os ids usados pelo callback, mas sem renderizar o bloco final repetitivo.
                    # A tabela de organismos agora fica ao lado da árvore, dentro de build_tree_column().
                    html.Div(
                        [
                            html.Div(id="learning-goal"),
                            html.Div(id="secondary-goal-copy"),
                            html.Div(id="secondary-description"),
                            html.Div(id="secondary-explanation"),
                        ],
                        id="secondary-content",
                        className="secondary-content-stack is-hidden",
                    ),
                ],
                className="example-shell",
            ),
        ],
        className="page",
    )

