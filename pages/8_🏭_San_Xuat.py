import streamlit as st
import pandas as pd
from datetime import date
import time
from db_utils import get_connection

st.set_page_config(page_title="Quản Lý Sản Xuất", page_icon="🏭", layout="wide")
st.header("🏭 Nhật Ký Vận Hành Máy Ép")
conn = get_connection()

tab1, tab2, tab3 = st.tabs(["📋 Sổ Theo Dõi Sản Xuất", "⚙️ Ghi Nhận Ca Máy", "📊 Hiệu Suất (OEE)"])

# --- TAB 1: SỔ THEO DÕI SẢN XUẤT ---
with tab1:
    st.subheader("Bảng Kê Sản Xuất Chi Tiết")
    df_sx = pd.read_sql("SELECT * FROM nhat_ky_san_xuat ORDER BY id DESC", conn)
    
    if not df_sx.empty:
        # Bộ lọc
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            loc_may = st.selectbox("Lọc theo Máy ép", ["Tất cả"] + df_sx['may_ep'].unique().tolist())
        with col_loc2:
            loc_tho = st.selectbox("Lọc theo Thợ", ["Tất cả"] + df_sx['ten_tho'].unique().tolist())
            
        df_hien_thi = df_sx.copy()
        if loc_may != "Tất cả":
            df_hien_thi = df_hien_thi[df_hien_thi['may_ep'] == loc_may]
        if loc_tho != "Tất cả":
            df_hien_thi = df_hien_thi[df_hien_thi['ten_tho'] == loc_tho]
            
        # Sắp xếp lại cột cho giống Excel của WANCHI
        df_hien_thi = df_hien_thi[['ngay', 'ca_lam_viec', 'may_ep', 'ten_tho', 'san_pham', 'mau_sac', 'so_rap', 'tong_shot', 'sl_ly_thuyet', 'phe_pham', 'thanh_pham', 'khoi_luong_sp', 'tong_kl', 'ghi_chu']]
        df_hien_thi.columns = ['NGÀY', 'CA', 'MÁY', 'THỢ', 'SẢN PHẨM', 'MÀU SẮC', 'SỐ RẬP', 'SỐ SHOT', 'SL LÝ THUYẾT', 'PHẾ PHẨM', 'THÀNH PHẨM', 'KL SP (g)', 'TỔNG KL (kg)', 'GHI CHÚ']
        
        # Định dạng số
        format_so = {'SỐ SHOT': '{:,.0f}', 'SL LÝ THUYẾT': '{:,.0f}', 'PHẾ PHẨM': '{:,.0f}', 'THÀNH PHẨM': '{:,.0f}', 'TỔNG KL (kg)': '{:,.2f}'}
        st.dataframe(df_hien_thi.style.format(format_so), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có nhật ký sản xuất nào được ghi nhận.")

# --- TAB 2: GHI NHẬN CA MÁY ---
with tab2:
    st.subheader("Cập Nhật Dữ Liệu Sau Ca Làm Việc")
    
    # Lấy danh sách sản phẩm và thợ từ DB
    df_sp = pd.read_sql("SELECT ten_sp FROM dm_san_pham", conn)
    df_tho = pd.read_sql("SELECT ten_nv FROM nhan_vien", conn)
    
    list_sp = df_sp['ten_sp'].tolist() if not df_sp.empty else ["Vui lòng thêm SP ở Danh Mục"]
    list_tho = df_tho['ten_nv'].tolist() if not df_tho.empty else ["Vui lòng thêm Thợ ở Nhân Sự"]
    
    with st.form("form_san_xuat"):
        col1, col2, col3 = st.columns(3)
        with col1:
            ngay = st.date_input("Ngày sản xuất", date.today())
            ca = st.selectbox("Ca làm việc", ["Ca 1", "Ca 2", "Ca 3"])
            may_ep = st.selectbox("Máy ép", ["Toshiba T1", "Toshiba T2", "Porcheson P1", "Porcheson P2", "Máy Khác"])
            tho = st.selectbox("Tên Thợ đứng máy", list_tho)
            
        with col2:
            san_pham = st.selectbox("Sản phẩm", list_sp)
            mau_sac = st.text_input("Màu sắc (VD: Đen, Trắng...)")
            so_rap = st.number_input("Số rập (Cavities)", min_value=1, value=2, step=1)
            kl_sp = st.number_input("Khối lượng 1 SP (gram)", min_value=0.0, step=1.0)
            
        with col3:
            tong_shot = st.number_input("Tổng số Shot ép", min_value=0, step=100)
            phe_pham = st.number_input("Số Phế phẩm (Cái)", min_value=0, step=1)
            ghi_chu = st.text_area("Ghi chú (Hư mốc, vệ sinh...)")
            
        submit_sx = st.form_submit_button("Lưu Nhật Ký Sản Xuất", type="primary")
        
        if submit_sx:
            # Tự động tính toán logic
            sl_ly_thuyet = tong_shot * so_rap
            thanh_pham = sl_ly_thuyet - phe_pham
            
            # Tính tổng khối lượng ra KG (vì khối lượng SP đang nhập là gram)
            tong_kl = ((thanh_pham + phe_pham) * kl_sp) / 1000 
            
            c = conn.cursor()
            c.execute("""INSERT INTO nhat_ky_san_xuat 
                         (ngay, ca_lam_viec, may_ep, ten_tho, san_pham, mau_sac, so_rap, tong_shot, sl_ly_thuyet, phe_pham, thanh_pham, khoi_luong_sp, tong_kl, ghi_chu)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (ngay.strftime("%Y-%m-%d"), ca, may_ep, tho, san_pham, mau_sac, so_rap, tong_shot, sl_ly_thuyet, phe_pham, thanh_pham, kl_sp, tong_kl, ghi_chu))
            conn.commit()
            
            st.success(f"✅ Đã ghi nhận ca máy {may_ep}. Thành phẩm đạt: {thanh_pham:,.0f} cái. Nhựa tiêu hao: {tong_kl:.2f} kg.")
            time.sleep(1.5)
            st.rerun()

# --- TAB 3: BÁO CÁO HIỆU SUẤT ---
with tab3:
    st.subheader("Báo Cáo Chất Lượng & Phế Phẩm")
    if not df_sx.empty:
        # Tính tỷ lệ lỗi = (Phế phẩm / Sản lượng lý thuyết) * 100
        df_sx['ty_le_loi'] = (df_sx['phe_pham'] / df_sx['sl_ly_thuyet']) * 100
        df_sx['ty_le_loi'] = df_sx['ty_le_loi'].fillna(0) # Xử lý trường hợp sl_ly_thuyet = 0
        
        col_b1, col_b2 = st.columns(2)
        
        with col_b1:
            st.markdown("**🚨 Máy ép có tỷ lệ phế phẩm cao nhất**")
            loi_theo_may = df_sx.groupby('may_ep')['ty_le_loi'].mean().reset_index().sort_values('ty_le_loi', ascending=False)
            st.bar_chart(loi_theo_may.set_index('may_ep'))
            
        with col_b2:
            st.markdown("**🏆 Top Thợ có năng suất cao nhất (Thành phẩm đạt)**")
            nang_suat_tho = df_sx.groupby('ten_tho')['thanh_pham'].sum().reset_index().sort_values('thanh_pham', ascending=False)
            st.bar_chart(nang_suat_tho.set_index('ten_tho'))
    else:
        st.info("Nhập dữ liệu ca máy để xem báo cáo hiệu suất.")