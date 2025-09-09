# pages/tabs/overview.py
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app_instance import app
from data import df

# Layout của riêng tab này

layout = html.Div([
    # dbc.Row([
    #     dbc.Col(dcc.Graph(id='bar-chart'), width=6),
    #     dbc.Col(dcc.Graph(id='pie-chart'), width=6),
    # ], className="mt-4 mb-4"),
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), width=6),
        dbc.Col(html.Div([
            html.H5("Dữ liệu chi tiết", className="text-center"),
            dash_table.DataTable(id='data-table', columns=[{"name": i, "id": i} for i in df.columns], page_size=10, style_cell={'textAlign': 'left'}, style_header={'fontWeight': 'bold'})
        ]), width=6),
    ]),
])

# --- 3. CALLBACK CHÍNH ---
@app.callback(
    # Output('bar-chart', 'figure'), Output('pie-chart', 'figure'),
    Output('line-chart', 'figure'), Output('data-table', 'data'),
    [Input('city-filter', 'value'), Input('fruit-filter', 'value'), Input('date-filter-mode', 'value'),
     Input('single-date-picker', 'date'), Input('range-date-picker', 'start_date'), Input('range-date-picker', 'end_date')]
)
def update_all_tabs(selected_city, selected_fruits, date_mode, single_date, start_date, end_date):
    # Lọc dữ liệu
    filtered_df = df.copy()
    if selected_city != 'All':
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    if selected_fruits:
        filtered_df = filtered_df[filtered_df['Fruit'].isin(selected_fruits)]
    if date_mode == 'Single':
        if single_date:
            filtered_df = filtered_df[filtered_df['Date'] == pd.to_datetime(single_date)]
    else:
        if start_date and end_date:
            filtered_df = filtered_df[(filtered_df['Date'] >= pd.to_datetime(start_date)) & (filtered_df['Date'] <= pd.to_datetime(end_date))]
    
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title_text="Không có dữ liệu", xaxis=dict(visible=False), yaxis=dict(visible=False))
        return empty_fig, empty_fig, empty_fig, [], empty_fig, empty_fig

    # --- TẠO CÁC OUTPUT CHO TAB 1 (ĐÃ HOÀN THIỆN) ---
    fig_bar = px.bar(filtered_df, x="Fruit", y="Amount", color="City", title="Sản lượng theo từng loại quả", barmode='group')
    fig_bar.update_layout(transition_duration=500)
    
    pie_data = filtered_df.groupby('City')['Amount'].sum().reset_index()
    fig_pie = px.pie(pie_data, names='City', values='Amount', title="Tỷ trọng sản lượng theo thành phố")
    fig_pie.update_layout(transition_duration=500)
    
    line_data = filtered_df.sort_values(by='Date')
    fig_line = px.line(line_data, x="Date", y="Amount", color="Fruit", title="Xu hướng sản lượng theo thời gian", markers=True)
    fig_line.update_layout(transition_duration=500)
    
    table_data = filtered_df.to_dict('records')

    return fig_bar, fig_pie, fig_line, table_data