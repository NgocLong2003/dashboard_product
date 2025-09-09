import plotly.express as px

# Example usage of the calculate_grouped_measure_by_employee function
# Replace with your desired month, year, product, and measure
month_to_analyze = '8'
year_to_analyze = '2025'
product_to_analyze = 'Sanfovet'
measure_to_analyze = 'Doanh thu' # Or 'Doanh số' or 'Dư nợ CK'

def calculate_grouped_measure_by_employee(df, month, year, product, measure):
    """
    Calculates the total of a specified measure for each employee for a specific month, year, and product,
    and sorts the results by region and total measure.

    Args:
        df (pd.DataFrame): The input DataFrame with sales data.
        month (str): The month for which to calculate the measure.
        year (str): The year for which to calculate the measure.
        product (str): The product for which to calculate the measure.
        measure (str): The measure to calculate ('Doanh số' or 'Doanh thu').

    Returns:
        pd.DataFrame: A DataFrame with the total of the specified measure by employee, sorted by region and total measure.
    """
    # Filter data for the specific month, year, and product
    df_filtered = df[(df['Tháng'] == month) & (df['Năm'] == year) & (df['Sản phẩm'] == product)].copy()

    # Group by employee and region and sum the specified measure
    grouped_measure_by_employee = df_filtered.groupby(['Miền', 'NVKD'])[measure].sum().reset_index()

    # Sort by region and total measure
    grouped_measure_by_employee_sorted = grouped_measure_by_employee.sort_values(by=['Miền', measure], ascending=[True, False])

    return grouped_measure_by_employee_sorted


def chart_bar(df, ):
    employee_data = calculate_grouped_measure_by_employee(
        df,
        month_to_analyze,
        year_to_analyze,
        product_to_analyze,
        measure_to_analyze
    )

    # Sort the data by Miền and then by the measure value for correct plotting order
    employee_data_sorted = employee_data.sort_values(by=['Miền', measure_to_analyze], ascending=[False, True])


    # Create a horizontal bar chart by swapping x and y
    fig = px.bar(
        employee_data_sorted, # Use the sorted data
        y='NVKD',  # Employee names on the y-axis
        x=measure_to_analyze, # Measure value on the x-axis
        color='Miền', # Color bars by region
        title=f'{measure_to_analyze} theo Nhân viên và Miền tháng {month_to_analyze} năm {year_to_analyze} cho sản phẩm {product_to_analyze}',
        labels={'NVKD': 'Nhân viên Kinh doanh', measure_to_analyze: measure_to_analyze, 'Miền': 'Miền'},
        barmode='group', # 'group' or 'stack' depending on desired visual
        text=employee_data_sorted[measure_to_analyze].apply(lambda x: f'{x/1e6:,.1f} triệu'), # Add text labels
        # Hide the legend
    )

    # Update layout for better readability and sorting
    # Use categoryorder and categoryarray to sort the y-axis for horizontal bar chart
    fig.update_layout(
        yaxis={
            'categoryorder': 'array',
            'categoryarray': employee_data_sorted['NVKD'].tolist() # Use the sorted NVKD list for y-axis order
        },
        xaxis_tickformat = ',.0f', # Format x-axis ticks if needed
        height=1000, # Example height in pixels
        bargap=0.05, # Reduce the gap between bars (default is 0.1 or 0.2 depending on Plotly version)
        xaxis={'visible': False, 'showticklabels': False} # Hide x-axis
    )

    # Update text position and font size
    fig.update_traces(textposition='outside', textfont=dict(size=14), showlegend=False) # Set text position to outside and increase font size


    return fig