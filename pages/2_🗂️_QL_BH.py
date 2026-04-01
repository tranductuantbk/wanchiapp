import streamlit as st
import pandas as pd
from db_utils import get_connection

st.set_page_config(page_title="Quản Lý", page_icon="🗂️", layout="wide")
st.header("🗂️ Sổ Dữ Liệu Bán Hàng")
conn = get_connection()

# Đọc toàn bộ dữ liệu đơn hàng
df = pd.read_sql("SELECT * FROM don_hang ORDER BY ngay DESC", conn)

if not df.empty:
    # Bộ lọc cơ bản
    col1, col2 = st.columns(2)
    with col1:
        kh_filter = st.selectbox("🔍 Lọc theo Khách hàng", ["Tất cả"] + df['ten_kh'].unique().tolist())
    with col2:
        sp_filter = st.selectbox("🔍 Lọc theo Sản phẩm", ["Tất cả"] + df['ten_sp'].unique().tolist())

    # Áp dụng bộ lọc
    if kh_filter != "Tất cả":
        df = df[df['ten_kh'] == kh_filter]
    if sp_filter != "Tất cả":
        df = df[df['ten_sp'] == sp_filter]

    # Format số liệu hiển thị đẹp mắt hơn
    format_mapping = {'don_gia': '{:,.0f}', 'doanh_thu': '{:,.0f}', 'tong_nvl': '{:,.0f}', 'tong_cong_ep': '{:,.0f}', 'loi_nhuan': '{:,.0f}'}
    st.dataframe(df.style.format(format_mapping), use_container_width=True, hide_index=True)

    # Nút xuất dữ liệu ra CSV
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Tải xuống dữ liệu (CSV)",
        data=csv,
        file_name='DuLieuBanHang_WANCHI.csv',
        mime='text/csv',
    )
else:
    st.info("Chưa có dữ liệu đơn hàng nào được ghi nhận.")