import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
def create_kpi_card(title, value_id, color):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="card-title text-muted"),
                html.H2(id=value_id, className=f"text-{color}"),
            ]
        )
    )

