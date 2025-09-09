# app_instance.py

import dash
import dash_bootstrap_components as dbc

# Link đến thư viện icon Font Awesome
FA = "https://use.fontawesome.com/releases/v5.15.4/css/all.css"

# Dòng quan trọng: Khởi tạo đối tượng Dash và gán nó vào biến tên là 'app' (chữ thường)
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
    suppress_callback_exceptions=True
)

# Dòng này cũng quan trọng để triển khai sau này
server = app.server