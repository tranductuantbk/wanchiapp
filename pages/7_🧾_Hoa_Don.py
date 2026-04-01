import streamlit as st
import pandas as pd
from datetime import date
from db_utils import get_connection

st.set_page_config(page_title="Theo Dõi Hóa Đơn", page_icon="🧾", layout="wide")
st.header("🧾 Bảng Kê Theo Dõi Hóa Đơn & Công Nợ")
conn = get_connection()

tab1, tab2, tab3 = st.tabs(["📋 Bảng Kê Hóa Đơn", "➕ Xuất Hóa Đơn Mới", "✅ Cập Nhật Thanh Toán"])

# --- TAB 1: BẢNG KÊ HÓA ĐƠN ---
with tab1:
    st.subheader("Theo dõi trạng thái thanh toán")
    df_hd = pd.read_sql("SELECT * FROM hoa_don ORDER BY id DESC", conn)
    
    if not df_hd.empty:
        # Bộ lọc trạng thái
        trang_thai_filter = st.radio("Lọc theo trạng thái:", ["Tất cả", "Chưa TT", "Đã TT"], horizontal=True)
        
        df_hien_thi = df_hd.copy()
        if trang_thai_filter != "Tất cả":
            df_hien_thi = df_hien_thi[df_hien_thi['trang_thai'] == trang_thai_filter]
        
        # Sắp xếp và format lại cột cho giống Excel của WANCHI
        df_hien_thi = df_hien_thi[['so_hd', 'khach_hang', 'truoc_thue', 'thue_gtgt', 'tong_cong', 'phuong_thuc', 'ngay_tt', 'trang_thai', 'ghi_chu']]
        df_hien_thi.columns = ['SỐ HĐ', 'KHÁCH HÀNG', 'GIÁ TRỊ TRƯỚC THUẾ', 'THUẾ GTGT', 'TỔNG CỘNG', 'TIỀN MẶT/CK', 'NGÀY TT', 'TRẠNG THÁI', 'GHI CHÚ']
        
        format_tien = {'GIÁ TRỊ TRƯỚC THUẾ': '{:,.0f}', 'THUẾ GTGT': '{:,.0f}', 'TỔNG CỘNG': '{:,.0f}'}
        
        # Tô màu trạng thái (Đã TT màu xanh, Chưa TT màu đỏ)
        def color_status(val):
            if val == 'Đã TT': return 'color: green; font-weight: bold;'
            if val == 'Chưa TT': return 'color: red; font-weight: bold;'
            return ''
        
        st.dataframe(df_hien_thi.style.format(format_tien).map(color_status, subset=['TRẠNG THÁI']), use_container_width=True, hide_index=True)
        
        # Thống kê nhanh công nợ
        tong_phai_thu = df_hd[df_hd['trang_thai'] == 'Chưa TT']['tong_cong'].sum()
        st.error(f"🚨 **Tổng công nợ khách hàng chưa thanh toán: {tong_phai_thu:,.0f} VNĐ**")
    else:
        st.info("Chưa có dữ liệu hóa đơn.")

# --- TAB 2: XUẤT HÓA ĐƠN MỚI ---
with tab2:
    st.subheader("Khai báo Hóa Đơn")
    df_kh = pd.read_sql("SELECT ten_kh FROM dm_khach_hang", conn)
    
    with st.form("form_tao_hd"):
        col1, col2 = st.columns(2)
        with col1:
            ngay_lap = st.date_input("Ngày lập HĐ", date.today())
            so_hd = st.text_input("Số HĐ (VD: 0000123)")
            khach_hang = st.selectbox("Khách hàng", df_kh['ten_kh'].tolist() if not df_kh.empty else ["Vui lòng thêm KH ở phần Danh Mục"])
        
        with col2:
            truoc_thue = st.number_input("Giá trị HĐ trước thuế (VNĐ)", min_value=0.0, step=100000.0)
            muc_thue = st.selectbox("Mức thuế GTGT (%)", [8, 10, 0, 5])
            ghi_chu = st.text_input("Ghi chú")
        
        submit_hd = st.form_submit_button("Lưu Hóa Đơn (Mặc định: Chưa TT)")
        
        if submit_hd and so_hd:
            thue_gtgt = truoc_thue * (muc_thue / 100)
            tong_cong = truoc_thue + thue_gtgt
            
            c = conn.cursor()
            try:
                c.execute("""INSERT INTO hoa_don 
                             (ngay_lap, so_hd, khach_hang, truoc_thue, thue_gtgt, tong_cong, phuong_thuc, ngay_tt, trang_thai, ghi_chu)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                          (ngay_lap.strftime("%Y-%m-%d"), so_hd, khach_hang, truoc_thue, thue_gtgt, tong_cong, "", "", "Chưa TT", ghi_chu))
                conn.commit()
                st.success(f"✅ Đã lưu Hóa đơn {so_hd}. Tổng cộng: {tong_cong:,.0f} đ.")
            except:
                conn.rollback()
                st.error(f"⚠️ Lỗi: Số Hóa đơn {so_hd} đã tồn tại trong hệ thống!")

# --- TAB 3: CẬP NHẬT THANH TOÁN ---
with tab3:
    st.subheader("Ghi nhận Khách hàng Thanh toán")
    if not df_hd.empty:
        # Chỉ lấy những hóa đơn "Chưa TT"
        ds_chua_tt = df_hd[df_hd['trang_thai'] == 'Chưa TT']['so_hd'].tolist()
        
        if ds_chua_tt:
            with st.form("form_thanh_toan"):
                hd_can_tt = st.selectbox("Chọn Số Hóa đơn cần thanh toán", ds_chua_tt)
                
                col_pt, col_ngay = st.columns(2)
                with col_pt:
                    phuong_thuc = st.radio("Phương thức", ["Chuyển khoản", "Tiền mặt"], horizontal=True)
                with col_ngay:
                    ngay_tt = st.date_input("Ngày thanh toán", date.today())
                
                submit_tt = st.form_submit_button("Xác nhận Đã Thanh Toán")
                
                if submit_tt:
                    c = conn.cursor()
                    c.execute("""UPDATE hoa_don 
                                 SET trang_thai = 'Đã TT', phuong_thuc = %s ngay_tt = %s 
                                 WHERE so_hd = %s""", 
                              (phuong_thuc, ngay_tt.strftime("%Y-%m-%d"), hd_can_tt))
                    conn.commit()
                    st.success(f"✅ Đã cập nhật thanh toán cho Hóa đơn {hd_can_tt}!")
        else:
            st.success("🎉 Tuyệt vời! Tất cả hóa đơn đều đã được thanh toán, không còn công nợ!")
