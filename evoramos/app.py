"""Bootstrap do app Dash EvoRamos."""

from dash import Dash

from frontend.callbacks import register_callbacks
from frontend.layout import create_layout

app = Dash(__name__, title="EvoRamos", update_title="Carregando...")
server = app.server

app.layout = create_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
