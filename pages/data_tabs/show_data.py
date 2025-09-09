from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
from data import df

layout = dbc.Card(
    dbc.CardBody(
        [
            html.P("Đây là toàn bộ dữ liệu gốc được sử dụng trong dashboard, được tải từ DataFrame.", className="card-text"),
            dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                page_size=20,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'fontWeight': 'bold'},
            )
        ]
    )
)