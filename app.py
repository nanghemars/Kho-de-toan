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

# --- XỬ LÝ QUERY PARAMS CHO LỚP ĐANG CHỌN ---
if "selected_class" not in st.session_state:
    st.session_state.selected_class = classes[0] if classes else ""

query_params = st.query_params
if "class" in query_params:
    requested_class = query_params["class"]
    if requested_class in classes:
        st.session_state.selected_class = requested_class

if not st.session_state.selected_class and classes:
    st.session_state.selected_class = classes[0]

# --- MÃ CSS: ĐỔI MÀU CHỮ TRẮNG SÁNG & SẮP XẾP GỌN GÀNG ---
st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
        }
        
        /* Thanh Menu Ngang */
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
            color: #ffffff !important; /* Màu chữ trắng sáng để dễ đọc */
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
        /* Mục đang được chọn (Active) */
        .nav-link-custom.active {
            background-color: #2e7d32 !important;
            color: #ffffff !important;
            border-bottom: 3px solid #ffeb3b; /* Viền vàng nổi bật */
        }

        /* Khung ô chọn đề nổi bật */
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
        st.warning("⚠️ Không tìm thấy file logo bắt đầu bằng chữ 'logo'.")
    
    st.markdown("---")
    st.markdown("### 📥 Thêm tài liệu mới")
    if classes:
        st.write("Chọn lớp muốn đưa file vào:")
        upload_class = st.selectbox("Chọn lớp upload", classes, key="up_class", label_visibility="collapsed")
        
        uploaded_file = st.file_uploader("Chọn file từ máy tính:", type=['pdf', 'docx', 'pptx'], label_visibility="collapsed")
        
        if uploaded_file is not None:
            upload_path = os.path.join(ROOT_DIR, upload_class)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            with open(os.path.join(upload_path, uploaded_file.name), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Đã tải lên: {uploaded_file.name}")
            st.rerun()
    else:
        st.info("Chưa có thư mục lớp học nào trong hệ thống.")

# ==================== KHU VỰC CHÍNH BÊN PHẢI ====================
if classes:
    # --- THANH MENU NGANG (ĐÃ THÊM target="_self" ĐỂ MỞ TRÊN CÙNG 1 TAB) ---
    nav_html = '<nav class="top-nav"><ul class="nav-list">'
    for cls in classes:
        active_class = "active" if st.session_state.selected_class == cls else ""
        nav_html += f'<li><a href="?class={urllib.parse.quote(cls)}" target="_self" class="nav-link-custom {active_class}">📚 {cls}</a></li>'
    nav_html += '</ul></nav>'
    st.markdown(nav_html, unsafe_allow_html=True)

    selected_class = st.session_state.selected_class
    class_path = os.path.join(ROOT_DIR, selected_class)
    
    if os.path.exists(class_path):
        pdf_files = sorted([f for f in os.listdir(class_path) if f.lower().endswith('.pdf')])
        
        if pdf_files:
            st.markdown(f"## 📄 Kho Tài Liệu & Đề Thi - {selected_class}")
            st.markdown("---")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown('<p class="select-label">📄 Chọn đề kiểm tra / bài giảng cần xem:</p>', unsafe_allow_html=True)
                selected_pdf = st.selectbox("Chọn đề", pdf_files, label_visibility="collapsed")
            
            if selected_pdf:
                file_path = os.path.join(class_path, selected_pdf)
                
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="📥 Tải file về máy",
                            data=f,
                            file_name=selected_pdf,
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                
                st.markdown("---")
                
                # Tạo link GitHub Raw
                encoded_class = urllib.parse.quote(selected_class)
                encoded_pdf = urllib.parse.quote(selected_pdf)
                pdf_url = f"https://raw.githubusercontent.com/nanghemars/Kho-de-toan/main/{encoded_class}/{encoded_pdf}"
                
                # --- TRÌNH XEM PDF.JS ---
                pdfjs_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file={urllib.parse.quote(pdf_url)}"
                
                pdf_display = f'''
                    <div style="width: 100%; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; overflow: hidden;">
                        <iframe src="{pdfjs_url}" width="100%" height="850px" style="border: none;"></iframe>
                    </div>
                '''
                st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.info(f"📂 Thư mục **{selected_class}** hiện chưa có file PDF nào.")
else:
    st.warning("⚠️ Chưa tìm thấy thư mục lớp học nào trong hệ thống.")
