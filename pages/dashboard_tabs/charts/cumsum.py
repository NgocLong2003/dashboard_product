import numpy as np
from plotly import graph_objects as go
from data import target_year

def chart_cumsum(df, product):
    # Dữ liệu bạn cung cấp
    months_2025 = df['Tháng'].unique().tolist()
    monthly_revenue_2025 = df.groupby('Tháng')['Doanh số'].sum().tolist()
    target_value = target_year['2025'][product]['Doanh thu']
    expect_value = target_value/ 12 * len(months_2025)

    num_target_segments = 12 # Vẫn dùng để tính toán vị trí vạch đánh dấu

    # --- Chuẩn bị dữ liệu cho biểu đồ lũy kế ---

    cumulative_sum = np.cumsum(monthly_revenue_2025)
    bases = [0] + list(cumulative_sum[:-1])
    total_revenue = cumulative_sum[-1]
    compare_expect_value = (total_revenue - expect_value)/expect_value * 100
    title_compare = f"{'Vượt' if compare_expect_value >= 0 else 'Chậm'} {abs(compare_expect_value):.2f}%"

    # --- Tạo Plotly Figure ---

    fig = go.Figure()

    # 1. Thêm các cột doanh thu hàng tháng
    monthly_x = months_2025
    monthly_y = monthly_revenue_2025
    monthly_base = bases
    monthly_text = [f'{val/1e9:,.1f} tỷ' for val in monthly_y]

    fig.add_trace(go.Bar(
        x=monthly_x,
        y=monthly_y,
        base=monthly_base,
        marker_color='#1f77b4',
        name='Doanh thu hàng tháng',
        text=monthly_text,
        textposition='auto',
        showlegend=False
    ))

    # 2. Thêm cột "Total"
    total_x = ['Lũy kế']
    total_y = [total_revenue]
    total_base = [0]
    # Display only the total value inside the bar
    total_text = [f'{total_revenue/1e9:,.1f} tỷ']


    fig.add_trace(go.Bar(
        x=total_x,
        y=total_y,
        base=total_base,
        marker_color='#2ca02c', # Màu xanh lá
        name='Tổng Doanh thu (Lũy kế)',
        text=total_text,
        textposition='inside', # Position text inside the bar
        showlegend=False
    ))

    # 3. Thêm cột "Mục tiêu" duy nhất
    fig.add_trace(go.Bar(
        x=['Mục tiêu'],
        y=[target_value],
        base=[0],
        marker_color='rgba(214, 39, 40, 0.9)', # Màu đỏ vừa và hơi mờ
        name='Mục tiêu Năm',
        text=f'{target_value/1e9:,.0f} tỷ', # Chỉ hiển thị tổng 583 tỷ ở trên cùng
        textposition='outside', # Hiển thị bên ngoài cột
        showlegend=False
    ))

    # 4. Thêm các vạch đánh dấu và số thứ tự mờ cho cột "Mục tiêu"
    segment_height = target_value / num_target_segments
    x_target_position_base = 1.95 # Vị trí X cho cột Mục tiêu (0 là T1, 1 là T2, ... ở đây là 'Mục tiêu' ở cuối)
                                # 'Mục tiêu' là index 10 nếu x_values là months_2025 + ['Total', 'Mục tiêu']

    annotations = []
    for i in range(num_target_segments):
        # Vị trí Y cho vạch đánh dấu
        y_position = (i + 1) * segment_height
        # Vị trí X cho vạch đánh dấu và số
        x_bar_center = len(months_2025) + 1 # Index of 'Mục tiêu' in x_values
        x_line_start = x_bar_center + 0.35 # Bắt đầu từ rìa phải cột
        x_line_end = x_bar_center + 0.45 # Kết thúc ngắn bên ngoài cột
        x_text_position = x_bar_center + 0.5 # Vị trí số (hơi lệch ra ngoài)

        # Thêm vạch kẻ nhỏ
        fig.add_shape(type="line",
            x0=x_line_start, y0=y_position, x1=x_line_end, y1=y_position,
            line=dict(color="rgba(0,0,0,0.4)", width=1),
            xref="x", yref="y"
        )

        # Thêm số thứ tự
        annotations.append(dict(
            x=x_text_position, y=y_position,
            text=str(i + 1),
            xref="x", yref="y",
            showarrow=False,
            font=dict(color="rgba(0,0,0,0.4)", size=9), # Màu chữ mờ
            xanchor="left",
            yanchor="middle"
        ))

    # Add horizontal line for expected cumulative target
    fig.add_shape(type="line",
        x0=0, y0=expect_value, x1=len(months_2025) + 2, y1=expect_value, # Extend line slightly beyond the last month bar
        line=dict(color="orange", width=2, dash="dash"),
        xref="x", yref="y"
    )

    # Add annotation for the expected cumulative target line
    annotations.append(dict(
        x=0.5, # Position at the end of the line
        y=expect_value,
        text=f'Mục tiêu Lũy kế ({len(months_2025)} tháng): {expect_value/1e9:,.2f} tỷ',
        xref="x", yref="y",
        showarrow=False,
        xanchor="left",
        yanchor="bottom",
        font=dict(color="orange", size=10)
    ))

    # Add annotation for title_compare above the 'Lũy kế' bar
    annotations.append(dict(
        x=len(months_2025), # X position of the 'Lũy kế' bar
        y=total_revenue, # Y position slightly above the top of the bar
        text=title_compare,
        xref="x", yref="y",
        showarrow=False,
        xanchor="center", # Center the text above the bar
        yanchor="bottom", # Position the text just above the bar
        font=dict(color="black", size=10) # Customize font color and size if needed
    ))


    fig.update_layout(annotations=annotations)


    # --- Tùy chỉnh Layout ---

    # fig.update_layout(
    #     title_text='Biểu đồ Doanh thu Lũy kế và Mục tiêu Năm 2025',
    #     xaxis_title='Tháng',
    #     yaxis_title='Doanh thu (tỷ VNĐ)',
    #     yaxis_tickformat='.0f',
    #     legend_title='Chú thích',
    #     template='plotly_white',
    #     barmode='overlay'
    # )

    # Định dạng trục Y để hiển thị giá trị theo đơn vị tỷ
    fig.update_yaxes(tickvals=np.arange(0, target_value * 1.1, 100e9),
                    ticktext=[f'{v/1e9:,.0f} tỷ' for v in np.arange(0, target_value * 1.1, 100e9)])

    # Sắp xếp lại trục x để 'Total' và 'Mục tiêu' ở cuối
    fig.update_xaxes(categoryorder='array', categoryarray=months_2025 + ['Lũy kế', 'Mục tiêu'])

    # --- Hiển thị và Lưu Biểu đồ ---
    return fig