import os
import streamlit as st
import urllib.parse
import base64
import re

# Cấu hình trang rộng
st.set_page_config(page_title="Top Giáo Dục - Lớp Toán Thầy Lộc", layout="wide")

# Lấy đường dẫn thư mục hiện tại
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
ROOT_DIR = current_dir

# Hàm hỗ trợ sắp xếp tên lớp theo đúng thứ tự số (6, 7, 8, 9, 10, 11, 12)
def sort_class_key(class_name):
    match = re.search(r'\d+', class_name)
    return int(match.group()) if match else 999

# Quét danh sách các lớp và sắp xếp từ lớp 6 đến lớp 12
classes = []
if os.path.exists(ROOT_DIR):
    raw_classes = [f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f)) and not f.startswith('.') and f != "__pycache__"]
    classes = sorted(raw_classes, key=sort_class_key)

# TỰ ĐỘNG TẠO SẴN 3 THƯ MỤC CON CHO TẤT CẢ CÁC LỚP ĐỂ KHÔNG BỊ LỖI THIẾU THƯ MỤC
for cls in classes:
    cls_path = os.path.join(ROOT_DIR, cls)
    for sub_folder in ["Bai_hoc", "BTVN", "Video"]:
        sub_path = os.path.join(cls_path, sub_folder)
        if not os.path.exists(sub_path):
            os.makedirs(sub_path, exist_ok=True)

# --- XỬ LÝ QUERY PARAMS CHO LỚP, TAB VÀ FILE ---
query_params = st.query_params
requested_class = query_params.get("class", None)
requested_tab = query_params.get("tab", "Bai_hoc")
requested_file = query_params.get("file", None)

if requested_class and requested_class in classes:
    st.session_state.selected_class = requested_class
else:
    if "selected_class" not in st.session_state or st.session_state.selected_class not in classes:
        st.session_state.selected_class = classes[0] if classes else ""

# Đồng bộ lại query params nếu có sự lệch pha
if "selected_class" in st.session_state and st.query_params.get("class") != st.session_state.selected_class:
    st.query_params.clear()
    st.query_params["class"] = st.session_state.selected_class

# --- MÃ CSS GIAO DIỆN ---
st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
        }
        .top-nav {
            background-color: #1b5e20;
            border-radius: 8px;
            padding: 0 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .nav-list {
            list-style: none;
            margin: 0;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        .nav-link-custom {
            display: block;
            padding: 12px 18px;
            color: #ffffff !important;
            text-decoration: none;
            font-weight: bold;
            font-size: 15px;
            text-transform: uppercase;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        .nav-link-custom:hover {
            background-color: #2e7d32;
            color: #ffffff !important;
        }
        .nav-link-custom.active {
            background-color: #2e7d32 !important;
            color: #ffffff !important;
            border-bottom: 3px solid #ffeb3b;
        }
        div[data-testid="stSelectbox"] > div {
            border: 2px solid #2e7d32 !important;
            border-radius: 10px !important;
            background-color: #f1f8e9 !important;
            box-shadow: 0px 3px 6px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stSelectbox"] svg {
            fill: #1b5e20 !important;
            width: 22px !important;
            height: 22px !important;
            transform: scale(1.2);
        }
        .select-label {
            font-size: 16px;
            font-weight: bold;
            color: #1b5e20;
            margin-bottom: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# ==================== THANH BÊN (SIDEBAR - UPLOAD & LOGO) ====================
with st.sidebar:
    logo_path = None
    for file in os.listdir(current_dir):
        if file.lower().startswith("logo"):
            logo_path = os.path.join(current_dir, file)
            break
            
    if logo_path:
        with open(logo_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{encoded_string}" style="width: 100%; mix-blend-mode: multiply;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("⚠️ Không tìm thấy file logo.")
    
    st.markdown("---")
    st.markdown("### 📥 Thêm tài liệu mới")
    if classes:
        st.write("Chọn lớp muốn đưa file vào:")
        current_selected = st.session_state.get("selected_class", classes[0])
        default_index = classes.index(current_selected) if current_selected in classes else 0
        
        upload_class = st.selectbox("Chọn lớp upload", classes, index=default_index, key="up_class", label_visibility="collapsed")
        
        upload_category = st.selectbox("Chọn mục:", ["Bài học trên lớp", "Bài tập về nhà (BTVN)", "Video bài giảng"], key="up_cat")
        cat_folder_map = {
            "Bài học trên lớp": "Bai_hoc",
            "Bài tập về nhà (BTVN)": "BTVN",
            "Video bài giảng": "Video"
        }
        sub_folder_name = cat_folder_map[upload_category]

        uploaded_file = st.file_uploader("Chọn file từ máy tính:", type=['pdf', 'docx', 'pptx', 'mp4'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            upload_path = os.path.join(ROOT_DIR, upload_class, sub_folder_name)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            with open(os.path.join(upload_path, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Đã tải lên mục {upload_category}: {uploaded_file.name}")
            st.rerun()
    else:
        st.info("Chưa có thư mục lớp học nào.")

# ==================== KHU VỰC CHÍNH BÊN PHẢI ====================
if classes:
    # --- THANH MENU NGANG CHỌN LỚP ---
    nav_html = '<nav class="top-nav"><ul class="nav-list">'
    for cls in classes:
        active_class = "active" if st.session_state.selected_class == cls else ""
        nav_html += f'<li><a href="?class={urllib.parse.quote(cls)}" target="_self" class="nav-link-custom {active_class}">📚 {cls}</a></li>'
    nav_html += '</ul></nav>'
    st.markdown(nav_html, unsafe_allow_html=True)

    selected_class = st.session_state.selected_class
    class_path = os.path.join(ROOT_DIR, selected_class)
    
    if os.path.exists(class_path):
        st.markdown(f"## 📄 Kho Tài Liệu & Đề Thi - {selected_class}")
        st.markdown("---")
        
        # Danh sách các tab và tên hiển thị tương ứng
        tab_keys = ["Bai_hoc", "BTVN", "Video"]
        tab_names = ["📚 Bài học trên lớp", "📝 Bài tập về nhà (BTVN)", "🎥 Video bài giảng"]
        
        default_tab_idx = 0
        if requested_tab in tab_keys:
            default_tab_idx = tab_keys.index(requested_tab)
            
        selected_tab_label = st.radio("Chọn danh mục:", tab_names, index=default_tab_idx, horizontal=True, label_visibility="collapsed")
        
        tab_map_reverse = {
            "📚 Bài học trên lớp": "Bai_hoc",
            "📝 Bài tập về nhà (BTVN)": "BTVN",
            "🎥 Video bài giảng": "Video"
        }
        folder_name = tab_map_reverse[selected_tab_label]
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        sub_path = os.path.join(class_path, folder_name)
        if os.path.exists(sub_path):
            files = sorted([f for f in os.listdir(sub_path) if not f.startswith('.')])
            
            if files:
                f_index = 0
                if requested_tab == folder_name and requested_file and requested_file in files:
                    f_index = files.index(requested_file)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<p class="select-label">📄 Chọn tài liệu mục {selected_tab_label}:</p>', unsafe_allow_html=True)
                    selected_file = st.selectbox(f"Chọn file {folder_name}", files, index=f_index, key=f"sel_{folder_name}", label_visibility="collapsed")
                
                if selected_file:
                    st.query_params["class"] = selected_class
                    st.query_params["tab"] = folder_name
                    st.query_params["file"] = selected_file
                    
                    file_path = os.path.join(sub_path, selected_file)
                    
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        with open(file_path, "rb") as f:
                            st.download_button(
                                label="📥 Tải file về máy",
                                data=f,
                                file_name=selected_file,
                                mime="application/octet-stream",
                                use_container_width=True,
                                key=f"dl_{folder_name}"
                            )
                    
                    st.markdown("---")
                    
                    encoded_file = urllib.parse.quote(selected_file)
                    file_url = f"https://raw.githubusercontent.com/nanghemars/Kho-de-toan/main/{urllib.parse.quote(selected_class)}/{folder_name}/{encoded_file}"
                    
                    if selected_file.lower().endswith(('.mp4', '.mov', '.avi')):
                        st.video(file_path)
                    else:
                        pdfjs_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={urllib.parse.quote(file_url)}"
                        pdf_display = f'''
                            <div style="width: 100%; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; overflow: hidden;">
                                <iframe src="{pdfjs_url}" width="100%" height="850px" style="border: none;"></iframe>
                            </div>
                        '''
                        st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"📂 Thư mục **{selected_tab_label}** này chưa có tài liệu nào.")
        else:
            st.info(f"📂 Chưa tạo thư mục nội dung cho phần này trên hệ thống.")
    else:
        st.warning(f"⚠️ Thư mục **{selected_class}** chưa tồn tại.")
else:
    st.warning("⚠️ Chưa tìm thấy thư mục lớp học nào trong hệ thống.")
