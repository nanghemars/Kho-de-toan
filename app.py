import os
import streamlit as st
import urllib.parse
import base64

# Cấu hình trang rộng
st.set_page_config(page_title="Top Giáo Dục - Lớp Toán Thầy Lộc", layout="wide")

# --- MÃ CSS TÙY CHỈNH: LOGO, KHUNG CHỌN ĐỀ VÀ MŨI TÊN ---
st.markdown("""
    <style>
        /* Khung ô chọn đề nổi bật */
        div[data-testid="stSelectbox"] > div {
            border: 2px solid #2e7d32 !important;
            border-radius: 10px !important;
            background-color: #f1f8e9 !important;
            box-shadow: 0px 3px 6px rgba(0,0,0,0.05) !important;
        }
        /* Phóng to và đổi màu mũi tên */
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

# ==================== THANH BÊN (SIDEBAR) ====================
with st.sidebar:
    current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
    
    # --- TỰ ĐỘNG TÌM VÀ XÓA NỀN TRẮNG LOGO (MIX-BLEND-MODE) ---
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
    st.markdown("### 📁 Danh Mục Lớp")
    
    ROOT_DIR = current_dir 
    
    if os.path.exists(ROOT_DIR):
        classes = sorted([f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f)) and not f.startswith('.') and f != "__pycache__"])
        
        if classes:
            selected_class = st.selectbox("Chọn lớp", classes, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("### 📥 Thêm tài liệu mới")
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

# ==================== KHU VỰC CHÍNH BÊN PHẢI ====================
if 'selected_class' in locals() and classes:
    class_path = os.path.join(ROOT_DIR, selected_class)
    if os.path.exists(class_path):
        pdf_files = sorted([f for f in os.listdir(class_path) if f.lower().endswith('.pdf')])
        
        if pdf_files:
            st.markdown(f"## 📚 Kho Tài Liệu & Đề Thi - {selected_class}")
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
                
                # --- SỬ DỤNG TRÌNH XEM PDF.JS (HỖ TRỢ ZOOM, TRƯỢT, XEM TRỰC TIẾP CỰC KỲ MƯỢT MÀ) ---
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
    st.warning("⚠️ Chưa tìm thấy thư mục lớp học nào.")
