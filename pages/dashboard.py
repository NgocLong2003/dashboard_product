import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

from app_instance import app
from data import all_products, df
# Import nội dung của TỪNG TAB
from pages.dashboard_tabs import overview, advanced, easy

mien_options = [
    {'label': 'Tất cả', 'value': 'All'},
    {'label': 'Bắc', 'value': 'Bắc'},
    {'label': 'Nam', 'value': 'Nam'}
]
product_options = all_products.append('All')
df['Date_temp'] = pd.to_datetime(df['Năm'] + '-' + df['Tháng'] + '-01')

# 2. Sắp xếp và tạo cột chuỗi 'mm/yyyy'
df_sorted = df.sort_values('Date_temp')
df_sorted['MonthYear'] = df_sorted['Date_temp'].dt.strftime('%m/%Y')

# 3. Lấy danh sách duy nhất các tháng/năm để làm options cho dropdown
month_year_options = [{'label': my, 'value': my} for my in df_sorted['MonthYear'].unique()]
# --- 2. PHẦN LAYOUT CHÍNH ---
layout = dbc.Container([
    html.H1("Dashboard Phân tích Tổng hợp", className="my-4 text-primary text-center"),

    # Thanh Filter dính ở trên cùng
    html.Div(id='filter-bar', children=[
        dbc.Card(dbc.CardBody([
            # --- PHẦN FILTER ĐÃ ĐƯỢC HOÀN THIỆN ---
            dbc.Row([
                dbc.Col([
                    html.H5("Lọc theo sản phẩm và vùng miền:"),
                    dcc.Dropdown(
                        id='product-filter',         
                        options=all_products,
                        multi=True,
                        placeholder="Chọn sản phẩm",
                        value=['Sanfovet'], # SỬA Ở ĐÂY: Giá trị mặc định là một danh sách
                        className="mt-2"), # Dropdown sản phẩm của bạn
                    
                    # --- DROPDOWN CẦN SỬA ---
                    dcc.Dropdown(
                        id='mien-filter', 
                        options=mien_options,
                        multi=True,
                        placeholder="Chọn vùng miền...",
                        value=['All'], # SỬA Ở ĐÂY: Giá trị mặc định là một danh sách
                        className="mt-2"
                    ),
                    
                ], width=4),
                dbc.Col([
    html.H5("2. Lọc theo thời gian:"),
    dcc.RadioItems(
        id='date-filter-mode',
        options=[
            {'label': 'Chọn tháng đơn lẻ', 'value': 'Single'},
            {'label': 'Chọn khoảng tháng', 'value': 'Range'}
        ],
        value='Single', # Mặc định là chọn khoảng
    ),
    
    # --- Vùng chứa Dropdown chọn tháng đơn (thay thế DatePickerSingle) ---
    html.Div(
        id='single-month-div',
        children=[
            dcc.Dropdown(
                id='single-month-dropdown',
                options=month_year_options,
                placeholder="Chọn một tháng...",
                value= '08/2025' if month_year_options else None
            )
        ],
        style={'display': 'none'}, # Mặc định ẩn đi nếu value='Range'
        className="mt-2"
    ),

    # --- Vùng chứa Dropdown chọn khoảng tháng (thay thế DatePickerRange) ---
    html.Div(
        id='range-month-div',
        children=[
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='start-month-dropdown',
                        options=month_year_options,
                        placeholder="Từ tháng...",
                        value=month_year_options[0]['value'] if month_year_options else None
                    ), width=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='end-month-dropdown',
                        options=month_year_options,
                        placeholder="Đến tháng...",
                        value=month_year_options[-1]['value'] if month_year_options else None
                    ), width=6
                ),
            ])
        ],
        className="mt-2"
    ),
], width=8),
            ])
        ]), className="mb-4")
    ]),

    #Cấu trúc Tabs
    dbc.Tabs(id="tabs-container", children=[
        dbc.Tab(label="Báo cáo Tổng quan", children=easy.layout),
        # dbc.Tab(label="Báo cáo Tổng quan", children=overview.layout),
        # dbc.Tab(label="Phân tích Nâng cao", children=advanced.layout),
    ]),
], fluid=True)


# --- 4. CALLBACK PHỤ ---
# Callback để ẩn/hiện các div chứa dropdown
@app.callback(
    Output('single-month-div', 'style'),
    Output('range-month-div', 'style'),
    Input('date-filter-mode', 'value')
)
def toggle_month_filters(mode):
    if mode == 'Single':
        return {'display': 'block'}, {'display': 'none'}
    else: # mode == 'Range'
        return {'display': 'none'}, {'display': 'block'}