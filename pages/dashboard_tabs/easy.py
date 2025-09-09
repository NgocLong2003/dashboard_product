# pages/tabs/overview.py

from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from app_instance import app
from data import df
from pages.dashboard_tabs.charts.cumsum import chart_cumsum
from pages.dashboard_tabs.charts.bar import chart_bar
from pages.dashboard_tabs.charts.waterfall import chart_waterfall
from pages.dashboard_tabs.charts.card import  create_kpi_card
# Layout của riêng tab này
layout = html.Div([
    dbc.Row([
        # Cho biểu đồ rộng hết cỡ để dễ nhìn
        dbc.Col(dcc.Graph(id='cumsum-chart'), width=12), 
    ], className="mt-4 mb-4"),
        dbc.Row([
        # Cho biểu đồ rộng hết cỡ để dễ nhìn
        dbc.Col(dcc.Graph(id='waterfall-chart'), width=12), 
    ], className="mt-4 mb-4"),
    dbc.Row([
        # Cho biểu đồ rộng hết cỡ để dễ nhìn
        dbc.Col(dcc.Graph(id='bar-chart'), width=12), 
    ], className="mt-4 mb-4"),
])


# --- CALLBACK ĐÃ ĐƯỢC SỬA LẠI HOÀN CHỈNH ---
@app.callback(
    Output('cumsum-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('waterfall-chart', 'figure'),
    
    # SỬA 1: Khai báo lại toàn bộ Input cho đúng với ID và thuộc tính
    [Input('product-filter', 'value'),
     Input('mien-filter', 'value'), 
     Input('date-filter-mode', 'value'),
     Input('single-month-dropdown', 'value'),
     Input('start-month-dropdown', 'value'),
     Input('end-month-dropdown', 'value')]
)
# SỬA 2: Sắp xếp lại thứ tự và tên tham số cho đúng
def update_cumsum_chart(selected_products, selected_mien, date_mode, single_month, start_month, end_month):
    filtered_df = df.copy()

    # --- SỬA 3: Viết lại toàn bộ logic lọc ---

    # Lọc theo sản phẩm (giả sử cột trong df là 'Product')
    if selected_products and 'All' not in selected_products:
        filtered_df = filtered_df[filtered_df['Sản phẩm'].isin(selected_products)]

    # Lọc theo vùng miền (giả sử cột trong df là 'Mien')
    if selected_mien and 'All' not in selected_mien:
        filtered_df = filtered_df[filtered_df['Miền'].isin(selected_mien)]

    # Lọc theo thời gian (dựa trên tháng/năm)
    if date_mode == 'Single':
        if single_month:
            # Tạo cột 'MonthYear' để so sánh 'mm/yyyy'
            filtered_df['MonthYear'] = pd.to_datetime(df['Date_temp']).dt.strftime('%m/%Y')
            filtered_df = filtered_df[filtered_df['MonthYear'] == single_month]
            filtered_df = filtered_df.drop(columns=['MonthYear'])
    else: # date_mode == 'Range'
        if start_month and end_month:
            start_date = pd.to_datetime(start_month, format='%m/%Y').to_period('M').to_timestamp('M')
            end_date = pd.to_datetime(end_month, format='%m/%Y').to_period('M').to_timestamp('M')
            filtered_df = filtered_df[(filtered_df['Date_temp'] >= start_date) & (filtered_df['Date_temp'] <= end_date)]
    
    # Xử lý trường hợp không có dữ liệu
    if filtered_df.empty:
        empty_fig = go.Figure()
        empty_fig.update_layout(title_text="Không có dữ liệu phù hợp", xaxis=dict(visible=False), yaxis=dict(visible=False))
        # SỬA 4: Chỉ trả về 1 giá trị vì chỉ có 1 Output
        return empty_fig

    # --- SỬA 5: Tạo biểu đồ từ dữ liệu ĐÃ LỌC ---
    # Ví dụ vẽ biểu đồ đường từ dữ liệu đã lọc
    # Bạn có thể thay bằng hàm chart_cumsum(filtered_df, ...) của bạn
    fig_cumsum = chart_cumsum(df, 'Sanfovet')
    fig_cumsum.update_layout(transition_duration=500)

    fig_bar = chart_bar(df)
    fig_bar.update_layout(transition_duration=500)

    fig_waterfall = chart_waterfall(df)
    fig_waterfall.update_layout(transition_duration=500)

    df_filtered = df[(df['Năm'] == '2025') & (df['Sản phẩm'] == 'Sanfovet')].copy()
    overall_growth = calculate_growth_rate(df_filtered, [], ['Doanh số', 'Doanh thu'])
    overall_growth_month = overall_growth.loc[f'{'2025'}-{int('8'):02d}-01', :].dropna()
    current_month_data = df_filtered[df_filtered['Tháng'] == '8'].groupby(['Năm', 'Tháng'])[['Doanh số', 'Doanh thu']].sum().loc[('2025', '8')]
        # Format and print overall growth
    for col in ['Doanh số', 'Doanh thu']:
        growth_rate = overall_growth_month.get(col)
        total_value = current_month_data.get(col)
        if growth_rate is not None and total_value is not None:
            indicator = '↑ Tăng' if growth_rate >= 0 else '↓ Giảm'
            print(f"{col} bán: Tổng: {total_value:,.0f} ({indicator} {growth_rate:.2f}%)")

    # SỬA 6: Chỉ trả về 1 giá trị
    return fig_cumsum, fig_bar, fig_waterfall


def calculate_growth_rate(df, group_cols, value_cols):
    """
    Calculates the month-over-month growth rate for specified value columns, grouped by specified columns and month.

    Args:
        df (pd.DataFrame): The input DataFrame with 'Tháng' and 'Năm' columns.
        group_cols (list): A list of columns to group by (e.g., ['Miền']).
        value_cols (list): A list of columns to calculate growth rate for (e.g., ['Doanh số', 'Doanh thu']).

    Returns:
        pd.DataFrame: A DataFrame with month-over-month growth rates.
    """
    # Combine 'Năm' and 'Tháng' into a datetime column for proper sorting
    df['Thời gian'] = pd.to_datetime(df['Năm'].astype(str) + '-' + df['Tháng'], format='%Y-%m')

    # Group by the specified columns and 'Thời gian' and sum the value columns
    if group_cols:
        df_grouped = df.groupby(group_cols + ['Thời gian'])[value_cols].sum().reset_index()
        # Sort by the grouping columns and time
        df_grouped_sorted = df_grouped.sort_values(by=group_cols + ['Thời gian'])

        # Group by specified columns and calculate the percentage change
        grouped_growth = df_grouped_sorted.groupby(group_cols)[value_cols].pct_change() * 100

        # Add the grouping columns back to the result
        for col in group_cols:
            grouped_growth[col] = df_grouped_sorted[col].values

        # Set the index
        grouped_growth['Thời gian'] = df_grouped_sorted['Thời gian'].values
        grouped_growth = grouped_growth.set_index(group_cols + ['Thời gian'])
    else:
        df_grouped = df.groupby(['Thời gian'])[value_cols].sum().reset_index()
        # Sort by time
        df_grouped_sorted = df_grouped.sort_values(by=['Thời gian'])

        # Calculate the percentage change
        grouped_growth = df_grouped_sorted[value_cols].pct_change() * 100

        # Set the index
        grouped_growth['Thời gian'] = df_grouped_sorted['Thời gian'].values
        grouped_growth = grouped_growth.set_index(['Thời gian'])


    return grouped_growth