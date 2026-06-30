"""Callbacks de upload/importação de sequências."""

from dash import Input, Output, State, no_update

from frontend.state import IMPORTED_EXAMPLE_ID
from src.custom_sequence_parser import build_uploaded_example


def register_upload_sequence_callbacks(app):
    @app.callback(
        Output("imported-example", "data"),
        Output("selected-example-id", "data", allow_duplicate=True),
        Output("game-mode", "data", allow_duplicate=True),
        Output("sequence-upload-status", "children"),
        Output("sequence-upload-status", "className"),
        Input("sequence-upload", "contents"),
        State("sequence-upload", "filename"),
        prevent_initial_call=True,
    )
    def import_sequences(contents: str | None, filename: str | None):
        if not contents:
            return no_update, no_update, no_update, no_update, no_update
        try:
            imported = build_uploaded_example(contents, filename, IMPORTED_EXAMPLE_ID)
        except ValueError as exc:
            return no_update, no_update, no_update, str(exc), "upload-status error"
        return imported, IMPORTED_EXAMPLE_ID, "free", f"{len(imported['organisms'])} sequências importadas. A árvore livre está pronta para anotação.", "upload-status success"

