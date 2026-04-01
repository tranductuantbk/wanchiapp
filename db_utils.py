import sqlite3

def get_connection():
    # Kết nối đến file SQLite, cho phép nhiều luồng (thread) truy cập
    return sqlite3.connect('wanchi_database.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tạo Bảng Danh mục Sản phẩm
    c.execute('''CREATE TABLE IF NOT EXISTS dm_san_pham (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ten_sp TEXT UNIQUE,
                    nhom_sp TEXT,
                    dinh_muc_nhua REAL,
                    don_gia_nhua REAL,
                    don_gia_cong REAL
                )''')
    
    # Tạo Bảng Danh mục Khách hàng
    c.execute('''CREATE TABLE IF NOT EXISTS dm_khach_hang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ten_kh TEXT UNIQUE,
                    nhom_kh TEXT
                )''')
    
    # Tạo Bảng Đơn hàng (Lưu trữ Transactional Data)
    c.execute('''CREATE TABLE IF NOT EXISTS don_hang (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ngay TEXT,
                    so_phieu TEXT,
                    ten_kh TEXT,
                    ten_sp TEXT,
                    so_luong INTEGER,
                    don_gia REAL,
                    doanh_thu REAL,
                    tong_nvl REAL,
                    tong_cong_ep REAL,
                    loi_nhuan REAL
                )''')
    # Thêm bảng Danh mục Vật tư (Hạt nhựa, màu, bao bì...)
    c.execute('''CREATE TABLE IF NOT EXISTS dm_vat_tu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ten_vat_tu TEXT UNIQUE,
                    loai_vat_tu TEXT
                )''')
    
    # Thêm bảng Lịch sử Giao dịch Kho (Nhập/Xuất)
    c.execute('''CREATE TABLE IF NOT EXISTS giao_dich_kho (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ngay TEXT,
                    loai_phieu TEXT,
                    loai_hang TEXT,
                    ten_hang TEXT,
                    so_luong REAL,
                    ghi_chu TEXT
                )''')
# Tạo bảng Hồ sơ Nhân viên
    c.execute('''CREATE TABLE IF NOT EXISTS nhan_vien (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ten_nv TEXT UNIQUE,
                    chuc_vu TEXT,
                    luong_co_ban REAL,
                    phu_cap_co_dinh REAL
                )''')
    
    # Tạo bảng Bảng Lương (Lưu trữ lương hàng tháng)
    c.execute('''CREATE TABLE IF NOT EXISTS bang_luong (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thang_nam TEXT,
                    ten_nv TEXT,
                    luong_co_ban REAL,
                    phu_cap REAL,
                    ngay_cong REAL,
                    thuong REAL,
                    phat REAL,
                    tam_ung REAL,
                    thuc_lanh REAL,
                    ghi_chu TEXT,
                    UNIQUE(thang_nam, ten_nv)
                )''')
# Tạo bảng Theo dõi Hóa đơn
    c.execute('''CREATE TABLE IF NOT EXISTS hoa_don (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ngay_lap TEXT,
                    so_hd TEXT UNIQUE,
                    khach_hang TEXT,
                    truoc_thue REAL,
                    thue_gtgt REAL,
                    tong_cong REAL,
                    phuong_thuc TEXT,
                    ngay_tt TEXT,
                    trang_thai TEXT,
                    ghi_chu TEXT
                )''')
# Tạo bảng Nhật ký Sản xuất
    c.execute('''CREATE TABLE IF NOT EXISTS nhat_ky_san_xuat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ngay TEXT,
                    ca_lam_viec TEXT,
                    may_ep TEXT,
                    ten_tho TEXT,
                    san_pham TEXT,
                    mau_sac TEXT,
                    so_rap INTEGER,
                    tong_shot INTEGER,
                    sl_ly_thuyet INTEGER,
                    phe_pham INTEGER,
                    thanh_pham INTEGER,
                    khoi_luong_sp REAL,
                    tong_kl REAL,
                    ghi_chu TEXT
                )''')
    conn.commit()
    conn.close()