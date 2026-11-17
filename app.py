import streamlit as st
import serial
import serial.tools.list_ports
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="Smart Futsal IoT Dashboard", page_icon="⚽", layout="wide")

# --- INISIALISASI STATE ---
for key, default in {
    "skor_a": 0,
    "skor_b": 0,
    "tim_a": "INFORMATIKA FC",
    "tim_b": "TEKNIK UNITED",
    "logs": [],
    "j_kiri": 0.0,
    "j_kanan": 0.0,
    "raw_serial": "Belum ada data masuk..."
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- SIDEBAR: KONTROL PERTANDINGAN & HARDWARE ---
with st.sidebar:
    st.header("🔌 Koneksi ESP32")
    ports = [port.device for port in serial.tools.list_ports.comports()]
    selected_port = st.selectbox("Port COM:", ports if ports else ["Tidak terdeteksi"])
    aktif_konek = st.toggle("Hubungkan ke ESP32", value=True)
    
    st.divider()
    st.header("⚽ Pengaturan Tim")
    st.session_state.tim_a = st.text_input("Nama Tim Kiri:", st.session_state.tim_a)
    st.session_state.tim_b = st.text_input("Nama Tim Kanan:", st.session_state.tim_b)
    
    tim_penyerang = st.radio(
        "Tim yang Menyerang Gawang IoT:",
        (st.session_state.tim_a, st.session_state.tim_b),
        help="Skor tim yang dipilih di sini akan bertambah +1 saat bola masuk ke gawang IoT."
    )
    
    st.divider()
    if st.button("🔄 Reset Pertandingan", type="primary", use_container_width=True):
        st.session_state.skor_a = 0
        st.session_state.skor_b = 0
        st.session_state.logs = []
        st.rerun()

# --- HEADER & PAPAN SKOR UTAMA ---
st.title("⚽ Smart Futsal Goal Detection Dashboard")
st.caption("Sistem Verifikasi Gol Otomatis Berbasis ESP32 & Dual-Sensor GSV")

col1, col2, col3 = st.columns([4, 1.5, 4])

with col1:
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center; margin-bottom: 0;'>{st.session_state.tim_a}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #FF4B4B; margin: 0;'>{st.session_state.skor_a}</h1>", unsafe_allow_html=True)
        c_a1, c_a2 = st.columns(2)
        if c_a1.button("➕ Gol", key="add_a", use_container_width=True):
            st.session_state.skor_a += 1
            st.rerun()
        if c_a2.button("➖ Koreksi", key="min_a", use_container_width=True) and st.session_state.skor_a > 0:
            st.session_state.skor_a -= 1
            st.rerun()

with col2:
    st.markdown("<h1 style='text-align: center; padding-top: 65px;'>VS</h1>", unsafe_allow_html=True)

with col3:
    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center; margin-bottom: 0;'>{st.session_state.tim_b}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 90px; color: #1C83E1; margin: 0;'>{st.session_state.skor_b}</h1>", unsafe_allow_html=True)
        c_b1, c_b2 = st.columns(2)
        if c_b1.button("➕ Gol", key="add_b", use_container_width=True):
            st.session_state.skor_b += 1
            st.rerun()
        if c_b2.button("➖ Koreksi", key="min_b", use_container_width=True) and st.session_state.skor_b > 0:
            st.session_state.skor_b -= 1
            st.rerun()

# --- MONITOR TELEMETRI SENSOR LIVE ---
st.subheader("📡 Status Sensor Gawang (Live)")
m1, m2, m3 = st.columns(3)
m1.metric("Ultrasonik Tiang Kiri", f"{st.session_state.j_kiri:.1f} cm", delta="Bola Dekat" if 0 < st.session_state.j_kiri < 20 else "Aman", delta_color="inverse")
m2.metric("Ultrasonik Tiang Kanan", f"{st.session_state.j_kanan:.1f} cm", delta="Bola Dekat" if 0 < st.session_state.j_kanan < 20 else "Aman", delta_color="inverse")
m3.metric("Data Terakhir ESP32", st.session_state.raw_serial)

st.divider()

# --- TABEL LOG KEJADIAN GOL ---
st.subheader("📋 Riwayat Gol Terverifikasi (GSV)")
if st.session_state.logs:
    df_logs = pd.DataFrame(st.session_state.logs)
    st.dataframe(df_logs, use_container_width=True, hide_index=True)
    csv = df_logs.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Unduh Log Laporan (CSV)", data=csv, file_name="log_gol_futsal.csv", mime="text/csv")
else:
    st.info("Menunggu bola melewati garis gawang...")

# --- PEMBACAAN SERIAL ESP32 ---
@st.cache_resource
def init_serial(port_name):
    try:
        ser = serial.Serial()
        ser.port = port_name
        ser.baudrate = 115200
        ser.timeout = 0.05
        ser.dtr = False
        ser.rts = False
        ser.open()
        return ser, None
    except Exception as e:
        return None, str(e)

if aktif_konek and selected_port != "Tidak terdeteksi":
    ser, err_msg = init_serial(selected_port)
    
    if err_msg:
        st.sidebar.error(f"Gagal buka {selected_port}: {err_msg}")
    elif ser and ser.is_open:
        st.sidebar.success(f"Terhubung: {selected_port}")
        try:
            while ser.in_waiting > 0:
                raw_line = ser.readline().decode('utf-8', errors='ignore').strip()
                if raw_line:
                    st.session_state.raw_serial = raw_line
                
                if raw_line.startswith("TELEMETRI|"):
                    parts = raw_line.split("|")
                    if len(parts) == 3:
                        st.session_state.j_kiri = float(parts[1])
                        st.session_state.j_kanan = float(parts[2])
                        
                elif raw_line.startswith("EVENT_GOL|"):
                    parts = raw_line.split("|")
                    j1 = float(parts[1]) if len(parts) > 1 else 0.0
                    j2 = float(parts[2]) if len(parts) > 2 else 0.0
                    waktu = datetime.now().strftime("%H:%M:%S")
                    
                    # Menambah skor sesuai tim yang dipilih di sidebar
                    if tim_penyerang == st.session_state.tim_a:
                        st.session_state.skor_a += 1
                        pencetak = st.session_state.tim_a
                    else:
                        st.session_state.skor_b += 1
                        pencetak = st.session_state.tim_b
                        
                    st.session_state.logs.insert(0, {
                        "Waktu": waktu,
                        "Tim Pencetak": pencetak,
                        "Skor Sementara": f"{st.session_state.skor_a} - {st.session_state.skor_b}",
                        "Jarak Kiri (cm)": j1,
                        "Jarak Kanan (cm)": j2,
                        "Status": "GOL VALID (GSV)"
                    })
                    st.toast(f"⚽ GOL UNTUK {pencetak}!", icon="🎉")
        except Exception as e:
            st.sidebar.warning(f"Error baca serial: {e}")

    time.sleep(0.25)
    st.rerun()