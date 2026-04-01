import streamlit as st
import psycopg2

def get_connection():
    # Kéo chìa khóa bảo mật từ Streamlit Secrets
    return psycopg2.connect(st.secrets["NEON_URL"])

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tạo Bảng Danh mục
    c.execute('''CREATE TABLE IF NOT EXISTS dm_san_pham (
                    id SERIAL PRIMARY KEY,
                    ten_sp TEXT UNIQUE,
                    nhom_sp TEXT,
                    dinh_muc_nhua FLOAT,
                    don_gia_nhua FLOAT,
                    don_gia_cong FLOAT
                )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS dm_khach_hang (
                    id SERIAL PRIMARY KEY,
                    ten_kh TEXT UNIQUE,
                    nhom_kh TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS dm_vat_tu (
                    id SERIAL PRIMARY KEY,
                    ten_vat_tu TEXT UNIQUE,
                    loai_vat_tu TEXT
                )''')
    
    # Tạo Bảng Quản lý
    c.execute('''CREATE TABLE IF NOT EXISTS don_hang (
                    id SERIAL PRIMARY KEY,
                    ngay TEXT,
                    so_phieu TEXT,
                    ten_kh TEXT,
                    ten_sp TEXT,
                    so_luong INTEGER,
                    don_gia FLOAT,
                    doanh_thu FLOAT,
                    tong_nvl FLOAT,
                    tong_cong_ep FLOAT,
                    loi_nhuan FLOAT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS giao_dich_kho (
                    id SERIAL PRIMARY KEY,
                    ngay TEXT,
                    loai_phieu TEXT,
                    loai_hang TEXT,
                    ten_hang TEXT,
                    so_luong FLOAT,
                    ghi_chu TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS nhan_vien (
                    id SERIAL PRIMARY KEY,
                    ten_nv TEXT UNIQUE,
                    chuc_vu TEXT,
                    luong_co_ban FLOAT,
                    phu_cap_co_dinh FLOAT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS bang_luong (
                    id SERIAL PRIMARY KEY,
                    thang_nam TEXT,
                    ten_nv TEXT,
                    luong_co_ban FLOAT,
                    phu_cap FLOAT,
                    ngay_cong FLOAT,
                    thuong FLOAT,
                    phat FLOAT,
                    tam_ung FLOAT,
                    thuc_lanh FLOAT,
                    ghi_chu TEXT,
                    UNIQUE(thang_nam, ten_nv)
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS hoa_don (
                    id SERIAL PRIMARY KEY,
                    ngay_lap TEXT,
                    so_hd TEXT UNIQUE,
                    khach_hang TEXT,
                    truoc_thue FLOAT,
                    thue_gtgt FLOAT,
                    tong_cong FLOAT,
                    phuong_thuc TEXT,
                    ngay_tt TEXT,
                    trang_thai TEXT,
                    ghi_chu TEXT
                )''')
                
    c.execute('''CREATE TABLE IF NOT EXISTS nhat_ky_san_xuat (
                    id SERIAL PRIMARY KEY,
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
                    khoi_luong_sp FLOAT,
                    tong_kl FLOAT,
                    ghi_chu TEXT
                )''')
    
    conn.commit()
    conn.close()
