from fpdf import FPDF
import os
import streamlit as st
import pandas as pd
from datetime import date
from db_utils import get_connection

st.set_page_config(page_title="Nhân Sự & Tiền Lương", page_icon="👥", layout="wide")
st.header("👥 Quản Lý Nhân Sự & Tiền Lương")
conn = get_connection()

tab1, tab2, tab3 = st.tabs(["📋 Danh Sách Nhân Viên", "💰 Chấm Công & Tính Lương", "🖨️ In Phiếu Lương"])

# --- TAB 1: DANH SÁCH NHÂN VIÊN ---
with tab1:
    st.subheader("Khai báo nhân viên mới")
    with st.form("form_nv"):
        col1, col2 = st.columns(2)
        with col1:
            ten_nv = st.text_input("Họ và Tên Nhân Viên")
            chuc_vu = st.text_input("Vị trí / Chức vụ (VD: Thợ ép, Kế toán...)")
        with col2:
            luong_cb = st.number_input("Lương cơ bản (VNĐ/tháng)", min_value=0.0, step=100000.0)
            phu_cap = st.number_input("Phụ cấp cố định (VNĐ/tháng)", min_value=0.0, step=50000.0)
            
        submit_nv = st.form_submit_button("Lưu Hồ Sơ")
        if submit_nv and ten_nv:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO nhan_vien (ten_nv, chuc_vu, luong_co_ban, phu_cap_co_dinh) VALUES (?, ?, ?, ?)", 
                          (ten_nv, chuc_vu, luong_cb, phu_cap))
                conn.commit()
                st.success(f"Đã thêm nhân viên: {ten_nv}")
            except:
                st.error("Lỗi: Tên nhân viên này đã tồn tại!")

    st.markdown("---")
    st.write("**Danh sách Nhân sự WANCHI**")
    df_nv = pd.read_sql("SELECT * FROM nhan_vien", conn)
    if not df_nv.empty:
        format_luong = {'luong_co_ban': '{:,.0f}', 'phu_cap_co_dinh': '{:,.0f}'}
        st.dataframe(df_nv.style.format(format_luong), use_container_width=True, hide_index=True)

# --- TAB 2: CHẤM CÔNG & TÍNH LƯƠNG ---
with tab2:
    st.subheader("Cập nhật Bảng Lương Tháng")
    if df_nv.empty:
        st.warning("Vui lòng thêm nhân viên ở tab Danh Sách Nhân Viên trước.")
    else:
        with st.form("form_tinh_luong"):
            col_thang, col_ten = st.columns(2)
            with col_thang:
                # Tạo format tháng/năm (VD: 03/2026)
                thang_hien_tai = date.today().strftime("%m/%Y")
                thang_nam = st.text_input("Kỳ lương (Tháng/Năm)", value=thang_hien_tai)
            with col_ten:
                nv_chon = st.selectbox("Chọn nhân viên", df_nv['ten_nv'].tolist())
            
            # Lấy thông tin lương cứng của người được chọn để làm cơ sở tính
            nv_info = df_nv[df_nv['ten_nv'] == nv_chon].iloc[0]
            luong_cb_hien_tai = nv_info['luong_co_ban']
            phu_cap_hien_tai = nv_info['phu_cap_co_dinh']
            
            st.markdown(f"*Lương cơ bản: **{luong_cb_hien_tai:,.0f} đ** | Phụ cấp: **{phu_cap_hien_tai:,.0f} đ***")
            
            col_cong, col_thuong, col_phat, col_ung = st.columns(4)
            with col_cong:
                ngay_cong = st.number_input("Số ngày công thực tế", min_value=0.0, max_value=31.0, value=26.0, step=0.5)
            with col_thuong:
                thuong = st.number_input("Thưởng (VNĐ)", min_value=0.0, step=50000.0)
            with col_phat:
                phat = st.number_input("Phạt / Trừ lương (VNĐ)", min_value=0.0, step=50000.0)
            with col_ung:
                tam_ung = st.number_input("Đã tạm ứng (VNĐ)", min_value=0.0, step=50000.0)
            
            ghi_chu = st.text_input("Ghi chú (Tùy chọn)")
            
            submit_luong = st.form_submit_button("Lưu & Tính Lương")
            
            if submit_luong:
                # Giả định chuẩn 26 ngày công/tháng. Bạn có thể thay đổi số 26 này nếu xưởng tính 30 ngày.
                luong_theo_cong = (luong_cb_hien_tai / 26) * ngay_cong
                thuc_lanh = luong_theo_cong + phu_cap_hien_tai + thuong - phat - tam_ung
                
                c = conn.cursor()
                try:
                    c.execute("""INSERT INTO bang_luong 
                                 (thang_nam, ten_nv, luong_co_ban, phu_cap, ngay_cong, thuong, phat, tam_ung, thuc_lanh, ghi_chu)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                              (thang_nam, nv_chon, luong_cb_hien_tai, phu_cap_hien_tai, ngay_cong, thuong, phat, tam_ung, thuc_lanh, ghi_chu))
                    conn.commit()
                    st.success(f"✅ Đã lưu lương tháng {thang_nam} cho {nv_chon}. Thực lãnh: {thuc_lanh:,.0f} VNĐ")
                except:
                    st.error(f"⚠️ Lỗi: Nhân viên {nv_chon} đã được tính lương trong tháng {thang_nam} rồi! Hãy kiểm tra lại.")

# --- TAB 3: IN PHIẾU LƯƠNG (XUẤT PDF A5) ---
with tab3:
    st.subheader("Trích xuất Phiếu Lương (PDF khổ A5)")
    df_luong = pd.read_sql("SELECT * FROM bang_luong", conn)
    
    if not df_luong.empty:
        col_chon_thang, col_chon_nv = st.columns(2)
        with col_chon_thang:
            list_thang = df_luong['thang_nam'].unique().tolist()
            thang_in = st.selectbox("Chọn kỳ lương cần in", list_thang)
        with col_chon_nv:
            list_nv = df_luong[df_luong['thang_nam'] == thang_in]['ten_nv'].tolist()
            if list_nv:
                nv_in = st.selectbox("Chọn nhân viên cần in phiếu", list_nv)
            else:
                st.warning("Kỳ lương này chưa có dữ liệu.")
                nv_in = None
                
        if nv_in:
            data_in = df_luong[(df_luong['thang_nam'] == thang_in) & (df_luong['ten_nv'] == nv_in)].iloc[0]
            st.success(f"Đang chọn phiếu lương của **{nv_in}** (Kỳ: {thang_in}). Vui lòng bấm nút bên dưới để tạo file in.")
            
            # --- LOGIC TẠO FILE PDF A5 ---
            def create_pdf(data):
                pdf = FPDF(format='A5')
                pdf.add_page()
                
                # Kiểm tra xem bạn đã copy font chữ vào thư mục chưa
                if not (os.path.exists("arial.ttf") and os.path.exists("arialbd.ttf")):
                    st.error("🚨 LỖI: Không tìm thấy font chữ! Vui lòng copy file arial.ttf và arialbd.ttf vào thư mục WANCHI_APP.")
                    return None
                
                # Nạp font tiếng Việt
                pdf.add_font("Arial", "", "arial.ttf")
                pdf.add_font("Arial", "B", "arialbd.ttf")
                
                # Tiêu đề
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "PHIẾU LƯƠNG XƯỞNG NHỰA WANCHI", align="C", ln=True)
                
                pdf.set_font("Arial", "", 12)
                pdf.cell(0, 8, f"Kỳ lương: {data['thang_nam']}", align="C", ln=True)
                pdf.ln(5) # Cách dòng
                
                # Đường kẻ ngang
                pdf.set_line_width(0.3)
                pdf.line(10, pdf.get_y(), 138, pdf.get_y())
                pdf.ln(5)
                
                # Hàm hỗ trợ in từng dòng cho đẹp
                def add_row(label, value, is_bold=False):
                    pdf.set_font("Arial", "B" if is_bold else "", 12)
                    pdf.cell(65, 8, label, border=0)
                    pdf.cell(0, 8, str(value), border=0, align="R", ln=True)

                add_row("Họ và tên:", data['ten_nv'], is_bold=True)
                add_row("Lương cơ bản:", f"{data['luong_co_ban']:,.0f} đ")
                add_row("Ngày công thực tế:", f"{data['ngay_cong']} ngày")
                add_row("Phụ cấp:", f"{data['phu_cap']:,.0f} đ")
                add_row("Thưởng:", f"{data['thuong']:,.0f} đ")
                add_row("Phạt/Trừ lương:", f"- {data['phat']:,.0f} đ")
                add_row("Đã tạm ứng:", f"- {data['tam_ung']:,.0f} đ")
                
                pdf.ln(5)
                pdf.line(10, pdf.get_y(), 138, pdf.get_y())
                pdf.ln(5)
                
                # Tổng thực lãnh
                pdf.set_font("Arial", "B", 14)
                pdf.cell(65, 10, "THỰC LÃNH:", border=0)
                pdf.cell(0, 10, f"{data['thuc_lanh']:,.0f} VNĐ", border=0, align="R", ln=True)
                
                pdf.ln(15)
                
                # Chữ ký
                pdf.set_font("Arial", "B", 11)
                pdf.cell(64, 8, "Người lập phiếu", align="C")
                pdf.cell(64, 8, "Người nhận", align="C", ln=True)
                
                pdf.set_font("Arial", "", 10)
                pdf.cell(64, 5, "(Ký & ghi rõ họ tên)", align="C")
                pdf.cell(64, 5, "(Ký & ghi rõ họ tên)", align="C", ln=True)
                
               # Trả về file dưới dạng byte để tải xuống
                return bytes(pdf.output())

            # Nút bấm tạo và tải PDF
            pdf_bytes = create_pdf(data_in)
            
            if pdf_bytes:
                st.download_button(
                    label="📄 Tải Xuống Phiếu Lương (PDF Khổ A5)",
                    data=pdf_bytes,
                    file_name=f"Phieu_Luong_{nv_in.replace(' ', '_')}_{thang_in.replace('/', '_')}.pdf",
                    mime="application/pdf",
                    type="primary"
                )
    else:
        st.info("Chưa có dữ liệu bảng lương nào để in.")
