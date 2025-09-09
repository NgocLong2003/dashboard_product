# app.py
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os
import urllib.parse
from flask import request, jsonify
from werkzeug.utils import secure_filename

# Import app từ file trung gian và các layout từ các trang
from app_instance import app, server
from pages import dashboard, datasource
# from data import df # Bạn có thể bỏ dòng này nếu không dùng
# from pages.data_tabs import handle_data # Bỏ dòng này vì layout đã được nhúng trong datasource.py

# --- Bố cục tổng thể của ứng dụng ---

# 1. Định nghĩa Sidebar
sidebar = html.Div(
    [
        dbc.Button(id="open-sidebar-btn", n_clicks=0, children=[html.I(className="fas fa-bars")]),
        dbc.Offcanvas(
            id="sidebar",
            title="Menu",
            is_open=False,
            children=[
                dbc.Nav(
                    [
                        dbc.NavLink("Dashboard", href="/", active="exact"),
                        dbc.NavLink("Nguồn dữ liệu", href="/datasource", active="exact"),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ]
        ),
    ]
)

# 2. Bố cục chính
app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        sidebar,
        html.Div(id="page-content")
    ],
    fluid=True
)

# --- Các hàm CALLBACK ---

# 1. Callback để đóng/mở sidebar
@app.callback(
    Output("sidebar", "is_open"),
    Input("open-sidebar-btn", "n_clicks"),
    State("sidebar", "is_open"),
)
def toggle_sidebar(n1, is_open):
    if n1:
        return not is_open
    return is_open

# 2. Callback chính để điều hướng trang
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/datasource":
        return datasource.layout
    else:
        return dashboard.layout


# =====================================================================
# --- PHẦN API ENDPOINTS ĐÃ ĐƯỢC SỬA ĐỔI HOÀN TOÀN ---
# =====================================================================

DATA_SOURCE_DIR = "data_source"
BOX_NAMES = ['Viavet', 'Sanfovet', 'DufaFarm', 'Dự án', 'Xuất khẩu', 'NL&Premix&Thủy sản', 'TP BVSK', 'ViaProtic']

@server.route('/api/files/<category>', methods=['GET'])
def list_files_in_category(category):
    """API trả về danh sách file trong một thư mục con cụ thể."""
    safe_category = secure_filename(urllib.parse.unquote(category))
    category_path = os.path.join(DATA_SOURCE_DIR, safe_category)
    
    if not os.path.isdir(category_path):
        return jsonify({"error": f"Category '{safe_category}' not found"}), 404
        
    try:
        files = [f for f in os.listdir(category_path) if f.endswith('.xlsx')]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@server.route('/api/upload/<category>', methods=['POST'])
def upload_file_to_category(category):
    """API để upload file vào một thư mục con cụ thể."""
    safe_category = secure_filename(urllib.parse.unquote(category))
    category_path = os.path.join(DATA_SOURCE_DIR, safe_category)
    if not os.path.isdir(category_path):
        return jsonify({"error": f"Category '{safe_category}' not found"}), 404

    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(category_path, filename)
        try:
            file.save(filepath)
            return jsonify({"success": True, "filename": filename})
        except Exception as e:
            print(f"Error saving file '{filename}' to '{filepath}': {e}") # In lỗi ra terminal để debug
            return jsonify({"error": f"Server error while saving file: {e}"}), 500
    
    return jsonify({"error": "No file selected or filename is empty"}), 400

@server.route('/api/files/<category>/<filename>', methods=['DELETE'])
def delete_file_in_category(category, filename):
    """API để xóa một file trong một thư mục con cụ thể."""
    safe_category = secure_filename(urllib.parse.unquote(category))
    safe_filename = secure_filename(urllib.parse.unquote(filename))
    
    try:
        filepath = os.path.join(DATA_SOURCE_DIR, safe_category, safe_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"success": True, "filename": safe_filename})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Chạy server ---
if __name__ == '__main__':
    app.run(debug=True, port = 8050) # Sửa app.run thành app.run_server