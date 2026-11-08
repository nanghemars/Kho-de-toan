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
        
        # Xác định tab mặc định từ URL
        default_tab_idx = 0
        if requested_tab in tab_keys:
            default_tab_idx = tab_keys.index(requested_tab)
            
        # Sử dụng radio button được CSS ẩn giao diện hoặc st.radio tùy biến để điều khiển tab chính xác theo URL
        # Hoặc dùng cấu trúc phân đoạn lựa chọn danh mục rõ ràng:
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
                    # Cập nhật query params chính xác tuyệt đối lên URL
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
