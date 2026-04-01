import streamlit as st
from db_utils import init_db

# Cấu hình trang hiển thị toàn màn hình
st.set_page_config(page_title="WANCHI Management", page_icon="🏭", layout="wide")

# Tự động khởi tạo database nếu chưa có
init_db()

st.title("🏭 Hệ Thống Quản Lý Sản Xuất & Bán Hàng WANCHI")
st.markdown("""
Chào mừng đến với hệ thống quản lý nội bộ. Toàn bộ dữ liệu của bạn giờ đây được lưu trữ an toàn trong SQLite và xử lý tốc độ cao bằng Pandas.

Vui lòng chọn các module ở thanh menu bên trái để bắt đầu:
* **📝 1. Nhập Liệu:** Lên đơn hàng mới, hệ thống sẽ tự động tính toán giá vốn và lợi nhuận.
* **🗂️ 2. Quản Lý:** Xem lại danh sách đơn hàng, lọc tìm kiếm và xuất file CSV.
* **📊 3. Dashboard:** Báo cáo quản trị, biểu đồ trực quan tự động cập nhật.
* **⚙️ 4. Danh Mục:** Nơi cài đặt gốc cho thông tin khách hàng, sản phẩm và định mức chi phí.

*Lưu ý: Nếu đây là lần đầu sử dụng, vui lòng vào phần **⚙️ Danh Mục** để thiết lập dữ liệu vật tư và khách hàng trước.*
""")