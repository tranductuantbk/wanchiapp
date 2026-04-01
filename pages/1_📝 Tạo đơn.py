import streamlit as st
import pandas as pd
from datetime import date
from db_utils import get_connection

st.set_page_config(page_title="Nhập Liệu", page_icon="📝", layout="wide")
st.header("📝 Lên Đơn Hàng Mới")
conn = get_connection()

# Đọc danh mục để đưa vào Dropdown
df_sp = pd.read_sql("SELECT * FROM dm_san_pham", conn)
df_kh = pd.read_sql("SELECT * FROM dm_khach_hang", conn)

if df_sp.empty or df_kh.empty:
    st.warning("⚠️ Vui lòng cập nhật Danh Mục Khách Hàng và Sản Phẩm trước khi nhập đơn!")
else:
    with st.form("form_nhap_lieu"):
        col1, col2 = st.columns(2)
        with col1:
            ngay = st.date_input("Ngày giao dịch", date.today())
            so_phieu = st.text_input("Số phiếu (VD: 1374)")
            khach_hang = st.selectbox("Khách hàng", df_kh['ten_kh'].tolist())
        with col2:
            san_pham = st.selectbox("Sản phẩm", df_sp['ten_sp'].tolist())
            so_luong = st.number_input("Số lượng (Cái)", min_value=1, step=1)
            don_gia = st.number_input("Đơn giá Bán (VNĐ/Cái)", min_value=0.0, step=100.0)

        submit = st.form_submit_button("Lưu Đơn Hàng")

        if submit:
            # Rút trích định mức để tính toán ngầm
            sp_info = df_sp[df_sp['ten_sp'] == san_pham].iloc[0]
            
            # Logic tính toán y hệt quy trình của xưởng
            doanh_thu = so_luong * don_gia
            tong_nvl = so_luong * sp_info['dinh_muc_nhua'] * sp_info['don_gia_nhua']
            tong_cong_ep = so_luong * sp_info['don_gia_cong']
            loi_nhuan = doanh_thu - tong_nvl - tong_cong_ep

            c = conn.cursor()
            c.execute("""INSERT INTO don_hang
                         (ngay, so_phieu, ten_kh, ten_sp, so_luong, don_gia, doanh_thu, tong_nvl, tong_cong_ep, loi_nhuan)
                         VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s)""",
                      (ngay.strftime("%Y-%m-%d"), so_phieu, khach_hang, san_pham, so_luong, don_gia, doanh_thu, tong_nvl, tong_cong_ep, loi_nhuan))
            conn.commit()
            
            st.success("✅ Lưu đơn hàng thành công!")
            st.info(f"💰 Doanh thu: {doanh_thu:,.0f} VNĐ | 🧱 Giá vốn NVL & Ép: {tong_nvl + tong_cong_ep:,.0f} VNĐ | 📈 Lợi nhuận: {loi_nhuan:,.0f} VNĐ")
