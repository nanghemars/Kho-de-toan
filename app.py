import streamlit as st
import os
from PIL import Image
from streamlit_pdf_viewer import pdf_viewer

# Cấu hình trang web
st.set_page_config(page_title="Kho Đề & Bài Giảng Toán - Thầy Lộc", layout="wide", page_icon="📚")

# Lấy đường dẫn thư mục gốc chứa file app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Tìm file logo tự động trong thư mục
logo_path = None
for file in os.listdir(BASE_DIR):
    if file.lower().startswith("logo."):
        logo_path = os.path.join(BASE_DIR, file)
        break

title_color = "#15803d" # Màu xanh lá đậm mặc định cực đẹp (đồng bộ với chữ Lớp Toán Thầy Lộc)
img_logo = None

if logo_path and os.path.exists(logo_path):
    try:
        # Mở ảnh và tự động xóa phông nền trắng thành trong suốt
        img = Image.open(logo_path).convert('RGBA')
        datas = img.getdata()
        new_data = []
        for item in datas:
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                new_data.append((255, 255, 255, 0))
            else:
                new_data.append(item)
        img.putdata(new_data)
        img_logo = img

        # Trích xuất màu sắc đậm đà, sắc nét từ logo (tránh các pixel bị mờ nhạt)
        img_rgb = img.convert('RGB')
        img_small = img_rgb.resize((50, 50))
        colors = img_small.getcolors(2500)
        if colors:
            colors = sorted(colors, key=lambda x: x[0], reverse=True)
            for count, col in colors:
                r, g, b = col
                # Chỉ lấy màu có độ bão hòa và độ đậm tốt (không phải màu trắng, xám hay màu mờ nhạt)
                if (max(r, g, b) - min(r, g, b) > 40) and (max(r, g, b) < 220):
                    title_color = f"#{r:02x}{g:02x}{b:02x}"
                    break
    except Exception:
        pass

# Tùy chỉnh màu sắc tiêu đề chung bằng CSS động
st.markdown(f"""
    <style>
    h1 {{
        color: {title_color};
        border-bottom: 2px solid {title_color};
        padding-bottom: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# Cột bên trái: Logo & Danh mục phân loại
st.sidebar.header("🗂️ Danh Mục Tài Liệu")

if img_logo:
    st.sidebar.image(img_logo, use_container_width=True)
else:
    st.sidebar.info("💡 Mẹo: Chép file ảnh logo vào thư mục này để hiện logo.")

# Lấy danh sách các thư mục khối lớp
folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f)) and not f.startswith(".") and not f.startswith("__")]
folders.sort()

if folders:
    selected_folder = st.sidebar.selectbox("Chọn Khối Lớp / Chuyên Đề:", folders)
    
    # Tính năng: Tải file PDF lên trực tiếp từ web
    st.sidebar.divider()
    st.sidebar.subheader("📤 Thêm tài liệu mới")
    upload_target = st.sidebar.selectbox("Chọn lớp muốn đưa file vào:", folders, key="up_target")
    uploaded_file = st.sidebar.file_uploader("Chọn file PDF từ máy tính:", type="pdf")
    
    if uploaded_file is not None:
        save_path = os.path.join(BASE_DIR, upload_target, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.sidebar.success(f"Đã tải lên thành công: {uploaded_file.name}")
        st.rerun()
    
    st.sidebar.divider()
    
    # Lấy danh sách file PDF trong thư mục được chọn
    folder_path = os.path.join(BASE_DIR, selected_folder)
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    pdf_files.sort()
    
    # Ô tìm kiếm tài liệu nhanh
    search_term = st.sidebar.text_input("🔍 Tìm kiếm tên tài liệu:", "")
    if search_term:
        pdf_files = [f for f in pdf_files if search_term.lower() in f.lower()]

    if pdf_files:
        selected_file = st.sidebar.radio("Chọn Đề thi / Bài giảng:", pdf_files)
        file_path = os.path.join(folder_path, selected_file)
        
        # Tiêu đề tên file đang xem (Màu sắc đậm nét, ton-sur-ton với logo)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
                <h3 style="color: {title_color}; margin: 0; font-size: 1.3rem; font-weight: 600;">
                    📄 Đang xem: {selected_file}
                </h3>
            """, unsafe_allow_html=True)
        with col2:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="📥 Tải file PDF về máy",
                    data=f,
                    file_name=selected_file,
                    mime="application/pdf"
                )
        
        st.divider()
        
        # Hiển thị file PDF cực nét
        pdf_viewer(file_path, width=900, height=1000)
    else:
        st.warning("Thư mục này chưa có file PDF nào. Thầy hãy tải file lên ở khung bên trái nhé!")
else:
    st.info("Chưa tìm thấy các thư mục Lớp.")