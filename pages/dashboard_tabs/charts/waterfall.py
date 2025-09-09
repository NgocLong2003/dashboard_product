import numpy as np
from plotly import graph_objects as go

def chart_waterfall(df):
    # Prepare data for Outstanding Debt waterfall chart
    monthly_outstanding_debt = df.groupby('Tháng')['Dư nợ CK'].sum()

    # Calculate the monthly change in outstanding debt
    # The first month's value is the starting point
    monthly_debt_change = monthly_outstanding_debt.diff().fillna(monthly_outstanding_debt.iloc[0])

    # --- Prepare data for the waterfall chart ---
    months = monthly_debt_change.index.tolist()
    measure_types = ['relative'] * len(months)
    measure_types[0] = 'absolute' # The first value is the starting outstanding debt

    y_values = monthly_debt_change.values.tolist()

    # Add a total bar
    months.append('Tổng Dư nợ CK')
    measure_types.append('total')
    y_values.append(sum(y_values)) # The total outstanding debt

    # --- Create Plotly Figure for Outstanding Debt Waterfall Chart ---
    fig_debt = go.Figure(go.Waterfall(
        name="Dư nợ CK",
        orientation="v",
        x=months,
        textposition="outside",
        text=[f'{val/1e9:,.2f} tỷ' for val in y_values],
        y=y_values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        measure=measure_types,
        increasing={"marker":{"color":"#d62728"}}, # Softer red for increasing (more debt)
        decreasing={"marker":{"color":"#2ca02c"}}  # Softer green for decreasing (less debt)
    ))

    # --- Customize Layout for Outstanding Debt Waterfall Chart ---
    fig_debt.update_layout(
        title_text='Biểu đồ Biến động Dư nợ CK hàng tháng 2025',
        xaxis_title='Tháng',
        yaxis_title='Biến động Dư nợ CK (tỷ VNĐ)',
        yaxis_tickformat='.0f',
        showlegend=True
    )

    # Format Y-axis to display values in billions
    max_abs_debt = max(abs(monthly_outstanding_debt.max()), abs(monthly_outstanding_debt.min()))
    fig_debt.update_yaxes(tickvals=np.arange(-max_abs_debt * 1.1, max_abs_debt * 1.1, max_abs_debt / 5) if max_abs_debt > 0 else [0],
                        ticktext=[f'{v/1e9:,.0f} tỷ' for v in np.arange(-max_abs_debt * 1.1, max_abs_debt * 1.1, max_abs_debt / 5)] if max_abs_debt > 0 else ['0 tỷ'])


    # --- Display the chart ---
    return fig_debt