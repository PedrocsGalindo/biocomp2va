"""Componente de upload de sequências TXT/FASTA."""

from dash import dcc, html


def build_sequence_upload() -> dcc.Upload:
    return dcc.Upload(
        id="sequence-upload",
        children=html.Div([html.Strong("Importar sequências TXT"), html.Span("FASTA ou linhas no formato nome sequência")]),
        multiple=False,
        className="sequence-upload",
    )

