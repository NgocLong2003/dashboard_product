# pages/data_tabs/handle_data.py
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc

layout = dbc.Card(
    dbc.CardBody(
        [
            html.P("Nội dung dưới đây được nhúng trực tiếp từ file datasource.html.", className="card-text"),
            # Sử dụng Iframe để hiển thị file HTML
            html.Iframe(
                src="/assets/datasource.html",
                style={"height": "600px", "width": "100%", "border": "none"}
            )
        ]
    )
)

