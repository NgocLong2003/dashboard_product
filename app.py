# app.py

import dash
from dash import dcc, html
import plotly.express as px
from data import df

# Khởi tạo ứng dụng Dash
app = dash.Dash(__name__)

# Gán server cho Render sử dụng
server = app.server 

# --- Ví dụ về một ứng dụng Dash đơn giản ---


fig = px.bar(df, x="Fruit", y="Amount", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash on Render'),
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])
# ---------------------------------------------

# Dòng này chỉ cần thiết khi chạy local, không cần cho Render
if __name__ == '__main__':
    app.run_server(debug=True)