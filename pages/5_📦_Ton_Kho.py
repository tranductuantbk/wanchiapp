import streamlit as st
import pandas as pd
from datetime import date
from db_utils import get_connection

st.set_page_config(page_title="Quản Lý Tồn Kho", page_icon="📦", layout="wide")
st.header("📦 Quản Lý Kho Vật Tư & Thành Phẩm")
conn = get_connection()

tab1, tab2, tab3 = st.tabs(["📊 Tồn Kho Hiện Tại", "🔄 Nhập / Xuất Kho", "🕒 Lịch Sử Giao Dịch"])

# --- TAB 1: TỒN KHO HIỆN TẠI ---
with tab1:
    st.subheader("Báo Cáo Tồn Kho Theo Thời Gian Thực")
    df_kho = pd.read_sql("SELECT * FROM giao_dich_kho", conn)
    
    if not df_kho.empty:
        # Chuyển đổi số lượng: Nhập là số dương, Xuất là số âm
        df_kho['so_luong_tinh'] = df_kho.apply(lambda x: x['so_luong'] if x['loai_phieu'] == 'Nhập' else -x['so_luong'], axis=1)
        
        # Gom nhóm tính tổng tồn kho
        df_ton_kho = df_kho.groupby(['loai_hang', 'ten_hang'])['so_luong_tinh'].sum().reset_index()
        df_ton_kho.columns = ['Loại Hàng', 'Tên Hàng', 'Tồn Kho Cuối']
        
        col_vt, col_tp = st.columns(2)
        with col_vt:
            st.markdown("#### 🛢️ Kho Nguyên Vật Liệu (kg)")
            df_nhua = df_ton_kho[df_ton_kho['Loại Hàng'] == 'Vật tư (Hạt nhựa, màu...)']
            st.dataframe(df_nhua, use_container_width=True, hide_index=True)
            
        with col_tp:
            st.markdown("#### 🛍️ Kho Thành Phẩm (Cái/Lốc)")
            df_san_pham = df_ton_kho[df_ton_kho['Loại Hàng'] == 'Thành phẩm']
            st.dataframe(df_san_pham, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có dữ liệu tồn kho. Hãy thực hiện Nhập/Xuất kho ở Tab bên cạnh.")

# --- TAB 2: NHẬP / XUẤT KHO ---
with tab2:
    st.subheader("Tạo Phiếu Nhập / Xuất")
    
    # Lấy danh sách hàng hóa từ DB
    df_sp = pd.read_sql("SELECT ten_sp FROM dm_san_pham", conn)
    df_vt = pd.read_sql("SELECT ten_vat_tu FROM dm_vat_tu", conn)
    
    # Do Streamlit form không thể tự cập nhật list dropdown ngay lập tức, 
    # ta dùng các widget độc lập cho mượt mà
    col1, col2 = st.columns(2)
    with col1:
        ngay_gd = st.date_input("Ngày giao dịch", date.today(), key="ngay_kho")
        loai_phieu = st.radio("Loại Phiếu", ["Nhập", "Xuất"], horizontal=True)
        loai_hang = st.radio("Loại Hàng Hóa", ["Vật tư (Hạt nhựa, màu...)", "Thành phẩm"], horizontal=True)
    
    with col2:
        # Hiển thị list tương ứng với loại hàng được chọn
        danh_sach_hang = []
        if loai_hang == "Thành phẩm":
            danh_sach_hang = df_sp['ten_sp'].tolist() if not df_sp.empty else []
            don_vi = "(Cái/Lốc)"
        else:
            danh_sach_hang = df_vt['ten_vat_tu'].tolist() if not df_vt.empty else []
            don_vi = "(Kg)"
            
        ten_hang = st.selectbox(f"Tên Hàng Hóa", danh_sach_hang)
        so_luong = st.number_input(f"Số lượng {don_vi}", min_value=0.0, step=1.0)
        ghi_chu = st.text_input("Ghi chú (VD: Nhập nhựa mác P102-422M, Xuất hàng cho ĐL...)")
        
    if st.button("💾 Ghi Nhận Kho", type="primary"):
        if not ten_hang:
            st.error("⚠️ Lỗi: Không có tên hàng hóa! Vui lòng cập nhật ở trang Danh Mục.")
        elif so_luong <= 0:
            st.error("⚠️ Lỗi: Số lượng phải lớn hơn 0.")
        else:
            c = conn.cursor()
            c.execute("""INSERT INTO giao_dich_kho (ngay, loai_phieu, loai_hang, ten_hang, so_luong, ghi_chu)
                         VALUES (?, ?, ?, ?, ?, ?)""", 
                      (ngay_gd.strftime("%Y-%m-%d"), loai_phieu, loai_hang, ten_hang, so_luong, ghi_chu))
            conn.commit()
            st.success(f"✅ Đã ghi nhận {loai_phieu} {so_luong} {ten_hang} thành công!")
            st.rerun() # Tải lại trang để cập nhật số tồn kho lập tức

# --- TAB 3: LỊCH SỬ GIAO DỊCH ---
with tab3:
    st.subheader("Sổ Nhật Ký Kho")
    df_ls = pd.read_sql("SELECT * FROM giao_dich_kho ORDER BY id DESC", conn)
    if not df_ls.empty:
        st.dataframe(df_ls, use_container_width=True, hide_index=True)
    else:
        st.write("Sổ kho trống.")