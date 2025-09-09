# pages/datasource.py
from dash import html, dash_table, dcc
import dash_bootstrap_components as dbc
from data import df

from pages.data_tabs import handle_data, show_data



# Layout chính của trang, chứa các tab
layout = dbc.Container([
    html.H1("Nguồn Dữ liệu", className="my-4 text-primary"),
    
    dbc.Tabs(children=
        [   
            dbc.Tab(label="Full Data", children=handle_data.layout),
            dbc.Tab(label="Dữ liệu DataFrame",children=show_data.layout),
            
        ]
    )
], fluid=True)