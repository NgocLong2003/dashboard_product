import pandas as pd
from data_source import *
import os
import numpy as np
dates = pd.to_datetime(pd.date_range(start='2025-08-01', periods=10, freq='D'))
df = pd.DataFrame({
    "Date": dates.tolist() * 2,
    "Fruit": ["Apples", "Oranges", "Bananas", "Grapes", "Apples", "Oranges", "Bananas", "Grapes", "Pears", "Pears"] * 2,
    "Amount": [4, 1, 2, 2, 2, 4, 5, 3, 6, 4, 8, 2, 4, 4, 4, 8, 10, 6, 12, 8],
    "City": ["SF", "SF", "Montreal", "SF", "Montreal", "SF", "Montreal", "SF", "Montreal", "SF"] * 2
})

all_products = ['Viavet', 'Sanfovet', 'DufaFarm', 'Dự án', 'Xuất khẩu', 'NL&Premix&Thủy sản', 'TP BVSK', 'ViaProtic']
target_year = {
    '2025':{
                'Viavet': {'Doanh số': 200_000_000_000,'Doanh thu': 160_000_000_000},
                'Sanfovet': {'Doanh số': 90_000_000_000,'Doanh thu': 72_000_000_000},
                'DufaFarm': {'Doanh số': 116_880_000_000,'Doanh thu': 93_500_000_000},
                'Dự án': {'Doanh số': 87_500_000_000,'Doanh thu': 70_000_000_000},
                'Xuất khẩu': {'Doanh số': 55_800_000_000,'Doanh thu': 55_800_000_000},
                'NL&Premix&Thủy sản': {'Doanh số': 40_880_000_000,'Doanh thu': 32_700_000_000},
                'TP BVSK': {'Doanh số': 100_000_000_000,'Doanh thu': 100_000_000_000},
                'ViaProtic': {'Doanh số': 50_000_000_000,'Doanh thu': 50_000_000_000}
                }
    }

def process_sales_data(file_path, month, year, product):
    """
    Reads and processes sales data from an Excel file and adds a month column.

    Args:
        file_path (str): The path to the Excel file.
        month (str): The month to be added as a new column.

    Returns:
        pd.DataFrame: The processed DataFrame with the added month column.
    """

    # Read the entire Excel sheet to find the starting row
    xls = pd.ExcelFile(file_path)
    sheet_name = xls.sheet_names[0]
    df_temp = xls.parse(sheet_name, header=None)

    # Find the row index where the first column contains "Mã KH"
    start_row = df_temp[df_temp[0] == 'Mã KH'].index[0]

    # Read the data again, skipping rows until the start_row and setting the header
    df = xls.parse(sheet_name, skiprows=start_row)

    # Add 'Mark' column based on 'Tên KH'
    df['Mark'] = df['Tên KH'].apply(lambda x: 'Tổng QL' if 'Tổng QL' in str(x) else ('Tổng NVKD' if 'Tổng NVKD' in str(x) else ('Tổng GD' if 'Tổng GD' in str(x) else '')))

    # Extract 'NVKD', 'QL', 'GD' from 'Tên KH'
    def extract_name(name, mark):
        if mark == 'Tổng NVKD':
            return str(name).replace('Tổng NVKD', '').strip()
        elif mark == 'Tổng QL':
            return str(name).replace('Tổng QL', '').strip()
        elif mark == 'Tổng GD':
            return str(name).replace('Tổng GD', '').strip()
        else:
            return ''

    df['NVKD'] = df.apply(lambda row: extract_name(row['Tên KH'], row['Mark']) if row['Mark'] == 'Tổng NVKD' else '', axis=1)
    df['QL'] = df.apply(lambda row: extract_name(row['Tên KH'], row['Mark']) if row['Mark'] == 'Tổng QL' else '', axis=1)
    df['GD'] = df.apply(lambda row: extract_name(row['Tên KH'], row['Mark']) if row['Mark'] == 'Tổng GD' else '', axis=1)


    # Fill empty values in 'GD', 'QL', and 'NVKD'
    df['GD'] = df['GD'].replace('', np.nan).fillna(method='bfill')
    df['QL'] = df['QL'].replace('', np.nan).fillna(method='bfill')
    df['NVKD'] = df['NVKD'].replace('', np.nan).fillna(method='bfill')


    # Remove rows with 'Mark' not empty
    df = df[df['Mark'] == '']
    df.drop(columns=['Mark'], inplace=True)

    # Remove the last row
    df = df[:-1]

    # Add 'Miền' column based on 'GD'
    def assign_mien(gd):
        if gd == 'Trần Văn Độ':
            return 'Nam'
        elif gd == 'Phạm Văn Tráng':
            return 'Bắc'
        else:
            return ''

    df['Miền'] = df['GD'].apply(assign_mien)

    # Add the 'month' column
    df['Tháng'] = month
    df['Năm'] = year
    df['Sản phẩm'] = product

    # Rename columns
    df = df.rename(columns={
        "HB bị TL đến cuối tháng": "Trả lại",
        "Tiền TT đến cuối tháng": "Doanh thu",
        "DS BH đến cuối tháng": "Doanh số"
    })


    return df


link_product ={
    'Viavet': 'data_source\Viavet',
    'Sanfovet': 'data_source\Sanfovet',
    'DufaFarm': 'data_source\DufaFarm', 
    'Dự án': 'data_source\Duan', 
    'Xuất khẩu': 'data_source\Xuatkhau', 
    'NL&Premix&Thủy sản': 'data_source\Thuysan', 
    'TP BVSK': 'data_source\TPBVSK', 
    'ViaProtic': 'data_source\ViaProtic'
}

df = pd.DataFrame()
for i in link_product:
    source = os.listdir(link_product[i])
    for file in source:
        year = file.split('_')[1].split('.')[0]
        month = file.split('_')[0]
        file_path = os.path.join(link_product[i],file)
        processed_df = process_sales_data(file_path, month, year, i)
        df = pd.concat([df, processed_df])
        last_month = i

print(df.shape)
