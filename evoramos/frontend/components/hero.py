"""Hero principal do EvoRamos."""

from dash import html


def build_hero() -> html.Header:
    return html.Header(
        [
            html.Div(
                [
                    html.Span("BIOLOGIA + TECNOLOGIA", className="hero-kicker"),
                    html.Div(
                        [
                            html.H1(["Evo", html.Span("Ramos")]),
                        ],
                        className="hero-title-row",
                    ),
                    html.H2("Interprete árvores filogenéticas em modo aula, desafio e duelo."),
                    html.P("Compare sequências fictícias de DNA, explore relações evolutivas e descubra como diferentes eventos aparecem em uma árvore."),
                    html.A("Começar pelos exercícios", href="#exercicios", className="hero-button"),
                ],
                className="hero-content",
            ),
            html.Div([html.Div(base, className=f"dna-base base-{base.lower()}") for base in ["A", "T", "C", "G"]], className="hero-visual"),
        ],
        className="hero",
    )
