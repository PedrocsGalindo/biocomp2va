"""Callbacks de seleção de modo de uso."""

from dash import Input, Output, State, ctx

from frontend.state import GAME_MODES


def register_game_mode_callbacks(app):
    @app.callback(Output("game-mode", "data"), Input("mode-learning", "n_clicks"), Input("mode-solo", "n_clicks"), Input("mode-duel", "n_clicks"), Input("mode-free", "n_clicks"), State("game-mode", "data"), prevent_initial_call=True)
    def select_mode(_learning: int, _solo: int, _duel: int, _free: int, current: str) -> str:
        return ctx.triggered_id.replace("mode-", "") if ctx.triggered_id else current

    @app.callback(Output("mode-learning", "className"), Output("mode-solo", "className"), Output("mode-duel", "className"), Output("mode-free", "className"), Input("game-mode", "data"))
    def update_mode_classes(active: str) -> tuple[str, str, str, str]:
        return tuple("mode-card is-active" if mode == active else "mode-card" for mode in GAME_MODES)

