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
            dbc.Row([
                dbc.Col(dcc.Graph(id='histogram-chart'), width=6),
                dbc.Col(dcc.Graph(id='scatter-chart'), width=6),
            ], className="mt-4"),
        ])

# --- 3. CALLBACK CHÍNH ---
@app.callback(
    Output('histogram-chart', 'figure'), Output('scatter-chart', 'figure'),
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


    # --- TẠO CÁC OUTPUT CHO TAB 2 ---
    fig_hist = px.histogram(filtered_df, x="Amount", nbins=10, title="Phân phối của Sản lượng")
    fig_hist.update_layout(transition_duration=500)

    df_pivot = filtered_df.pivot_table(index='Date', columns='Fruit', values='Amount').reset_index()
    fig_scatter = go.Figure()
    if 'Apples' in df_pivot.columns and 'Oranges' in df_pivot.columns:
        fig_scatter = px.scatter(df_pivot, x="Apples", y="Oranges", title="Tương quan Sản lượng Táo vs. Cam", trendline="ols")
    else:
        fig_scatter.update_layout(title_text="Chọn Táo và Cam để xem tương quan")
    fig_scatter.update_layout(transition_duration=500)

    return fig_hist, fig_scatter