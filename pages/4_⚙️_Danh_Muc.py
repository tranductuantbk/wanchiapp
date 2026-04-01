import streamlit as st
import pandas as pd
from db_utils import get_connection

st.set_page_config(page_title="Danh Mục", page_icon="⚙️", layout="wide")
st.header("⚙️ Quản Lý Danh Mục Gốc")
conn = get_connection()

# Thêm tab thứ 3 cho Nguyên Vật Liệu
tab1, tab2, tab3 = st.tabs(["📦 Sản Phẩm & Định Mức", "🤝 Khách Hàng", "🛢️ Nguyên Vật Liệu"])

with tab1:
    st.subheader("Thêm Sản Phẩm Mới (Thành Phẩm)")
    with st.form("form_sp"):
        col1, col2 = st.columns(2)
        with col1:
            ten_sp = st.text_input("Tên Sản phẩm (VD: 2 Quai 78 Đen)")
            nhom_sp = st.text_input("Nhóm Sản phẩm (VD: CHO)")
        with col2:
            dinh_muc = st.number_input("Định mức nhựa/SP (kg)", min_value=0.0, format="%.4f")
            gia_nhua = st.number_input("Đơn giá nhựa (VNĐ/kg)", min_value=0.0)
            gia_cong = st.number_input("Đơn giá công ép (VNĐ/SP)", min_value=0.0)
        
        submit_sp = st.form_submit_button("Lưu Sản Phẩm")
        if submit_sp and ten_sp:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO dm_san_pham (ten_sp, nhom_sp, dinh_muc_nhua, don_gia_nhua, don_gia_cong) VALUES (%s, %s, %s, %s, %s)", 
                          (ten_sp, nhom_sp, dinh_muc, gia_nhua, gia_cong))
                conn.commit()
                st.success(f"Đã thêm sản phẩm: {ten_sp}")
            except:
                st.error("Lỗi: Sản phẩm này đã tồn tại trong hệ thống!")

    st.markdown("---")
    st.write("**Danh sách Sản phẩm hiện tại**")
    df_sp = pd.read_sql("SELECT * FROM dm_san_pham", conn)
    st.dataframe(df_sp, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Thêm Khách Hàng Mới")
    with st.form("form_kh"):
        ten_kh = st.text_input("Tên Khách hàng")
        nhom_kh = st.selectbox("Nhóm KH", ["Đại lý", "Khách lẻ", "Xuất chuyển", "Khác"])
        submit_kh = st.form_submit_button("Lưu Khách Hàng")
        if submit_kh and ten_kh:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO dm_khach_hang (ten_kh, nhom_kh) VALUES (%s, %s)", (ten_kh, nhom_kh))
                conn.commit()
                st.success(f"Đã thêm khách hàng: {ten_kh}")
            except:
                conn.rollback()
                st.error("Lỗi: Khách hàng này đã tồn tại!")
                
    st.markdown("---")
    st.write("**Danh sách Khách hàng hiện tại**")
    df_kh = pd.read_sql("SELECT * FROM dm_khach_hang", conn)
    st.dataframe(df_kh, use_container_width=True, hide_index=True)

# ĐÂY LÀ PHẦN MỚI THÊM VÀO
with tab3:
    st.subheader("Thêm Nguyên Vật Liệu Mới")
    with st.form("form_vt"):
        ten_vt = st.text_input("Tên Vật tư (VD: Nhựa ABS P102-422M)")
        loai_vt = st.selectbox("Phân loại", ["Hạt nhựa nguyên sinh", "Nhựa băm (Tái chế)", "Phẩm màu", "Bao bì", "Khác"])
        submit_vt = st.form_submit_button("Lưu Vật Tư")
        if submit_vt and ten_vt:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO dm_vat_tu (ten_vat_tu, loai_vat_tu) VALUES (%s, %s)", (ten_vt, loai_vt))
                conn.commit()
                st.success(f"Đã thêm vật tư: {ten_vt}")
            except:
                conn.rollback()
                st.error("Lỗi: Vật tư này đã tồn tại!")
                
    st.markdown("---")
    st.write("**Danh sách Vật tư hiện tại**")
    df_vt = pd.read_sql("SELECT * FROM dm_vat_tu", conn)
    st.dataframe(df_vt, use_container_width=True, hide_index=True)
