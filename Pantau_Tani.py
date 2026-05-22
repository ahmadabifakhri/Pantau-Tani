import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =========================
# KONFIGURASI HALAMAN
# =========================

st.set_page_config(
    page_title="Pantau Tani — Greenhouse",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem !important; }

    /* ══════════════════════════════════════════════════════════════════
       STRATEGI TEMA:
       Streamlit sudah inject CSS variables bawaan ke :root yang otomatis
       berganti saat tema Light/Dark diubah di Settings.
       Kita PETAKAN variabel kustom kita ke variabel Streamlit native,
       bukan redefine ulang — sehingga SELALU sinkron tanpa media query
       atau data-theme selector apapun.

       Streamlit native vars yang tersedia:
         --background-color          → bg utama app
         --secondary-background-color→ bg card/sidebar/widget
         --text-color                → teks utama
         --font                      → font utama
         --primary-color             → accent (biru/hijau sesuai config)

       Untuk warna semantik (ok/warn/danger) yang tidak ada di Streamlit,
       kita gunakan oklch() agar kontras terjamin di kedua tema.
    ══════════════════════════════════════════════════════════════════ */

    :root {
        /* ── Petakan ke Streamlit native ── */
        --c-bg:           var(--background-color);
        --c-card:         var(--secondary-background-color);
        --c-text-primary: var(--text-color);

        /* Derived dari Streamlit — diperkirakan cukup kontras di keduanya */
        --c-text-secondary: color-mix(in srgb, var(--text-color) 75%, transparent);
        --c-text-muted:     color-mix(in srgb, var(--text-color) 45%, transparent);
        --c-border:         color-mix(in srgb, var(--text-color) 12%, transparent);
        --c-border-muted:   color-mix(in srgb, var(--text-color) 18%, transparent);
        --c-border-div:     color-mix(in srgb, var(--text-color) 8%, transparent);
        --c-card-alt:       color-mix(in srgb, var(--secondary-background-color) 90%, var(--text-color) 10%);

        /* ── Warna semantik — kontras tinggi di light & dark ── */
        /* OK / Hijau: background tipis, teks gelap di light / terang di dark */
        --c-ok-strip:   #22C55E;
        --c-ok-border:  #86EFAC;
        --c-ok-bg:      color-mix(in srgb, #22C55E 15%, var(--secondary-background-color));
        --c-ok-text:    color-mix(in srgb, #15803D 100%, transparent);
        --c-ok-box-bg:  color-mix(in srgb, #22C55E 10%, var(--background-color));

        /* WARN / Amber */
        --c-warn-strip: #F59E0B;
        --c-warn-bg:    color-mix(in srgb, #F59E0B 15%, var(--secondary-background-color));
        --c-warn-text:  color-mix(in srgb, #92400E 100%, transparent);

        /* DANGER / Merah */
        --c-danger-strip: #EF4444;
        --c-danger-bg:    color-mix(in srgb, #EF4444 15%, var(--secondary-background-color));
        --c-danger-text:  color-mix(in srgb, #991B1B 100%, transparent);
        --c-danger-box:   color-mix(in srgb, #EF4444 10%, var(--background-color));
        --c-border-alert: color-mix(in srgb, #EF4444 40%, transparent);

        /* BIRU / Prediksi */
        --c-blue-bg:     color-mix(in srgb, #3B82F6 12%, var(--secondary-background-color));
        --c-blue-card:   var(--secondary-background-color);
        --c-blue-border: color-mix(in srgb, #3B82F6 35%, transparent);
        --c-blue-text:   color-mix(in srgb, #1D4ED8 100%, transparent);
        --c-blue-label:  color-mix(in srgb, #3B82F6 100%, transparent);
        --c-blue-val:    color-mix(in srgb, #1E40AF 100%, transparent);
        --c-blue-unit:   color-mix(in srgb, #60A5FA 100%, transparent);
        --c-blue-note:   color-mix(in srgb, #60A5FA 100%, transparent);

        /* INFO card */
        --c-info-bg:     color-mix(in srgb, #22C55E 10%, var(--secondary-background-color));
        --c-info-border: color-mix(in srgb, #22C55E 35%, transparent);
        --c-info-text:   color-mix(in srgb, #14532D 100%, transparent);
        --c-info-small:  color-mix(in srgb, #15803D 100%, transparent);
        --c-info-chip:   var(--secondary-background-color);

        /* Gauge */
        --c-gauge-bg:    color-mix(in srgb, var(--text-color) 15%, var(--background-color));
        --c-gauge-thumb: var(--secondary-background-color);

        /* Kontrol */
        --c-ctrl-bg:      var(--secondary-background-color);
        --c-ctrl-border:  color-mix(in srgb, var(--text-color) 12%, transparent);
        --c-ctrl-title:   color-mix(in srgb, var(--text-color) 50%, transparent);
        --c-ctrl-divider: color-mix(in srgb, var(--text-color) 8%, transparent);

        /* Prediksi status text */
        --c-pred-ok:     #16A34A;
        --c-pred-warn:   #D97706;
        --c-pred-danger: #DC2626;

        /* card alert */
        --c-card-alert: color-mix(in srgb, #EF4444 8%, var(--secondary-background-color));
    }

    /* ══════════════════════════════════════════════════════════════════
       DARK MODE OVERRIDES
       Hanya warna semantik yang perlu di-flip kontrasnya (teks gelap
       jadi terang, background terang jadi gelap).
       Background & card sudah otomatis via Streamlit vars.
    ══════════════════════════════════════════════════════════════════ */
    [data-theme="dark"],
    @media (prefers-color-scheme: dark) { :root {
        --c-ok-text:      #86EFAC;
        --c-warn-text:    #FDE68A;
        --c-danger-text:  #FCA5A5;
        --c-blue-text:    #93C5FD;
        --c-blue-val:     #BFDBFE;
        --c-info-text:    #86EFAC;
        --c-info-small:   #4ADE80;
        --c-pred-ok:      #4ADE80;
        --c-pred-warn:    #FCD34D;
        --c-pred-danger:  #F87171;
    } }

    [data-theme="dark"] {
        --c-ok-text:      #86EFAC;
        --c-warn-text:    #FDE68A;
        --c-danger-text:  #FCA5A5;
        --c-blue-text:    #93C5FD;
        --c-blue-val:     #BFDBFE;
        --c-info-text:    #86EFAC;
        --c-info-small:   #4ADE80;
        --c-pred-ok:      #4ADE80;
        --c-pred-warn:    #FCD34D;
        --c-pred-danger:  #F87171;
    }

    /* ══════════════════════════════════════════════════════════════════
       STREAMLIT NATIVE ELEMENT — tidak di-override background-nya
       agar Streamlit bebas mengelola sendiri sesuai tema.
       Kita hanya rapikan border-radius, font, dan spacing.
    ══════════════════════════════════════════════════════════════════ */

    /* Expander */
    [data-testid="stExpander"] {
        border: 1.5px solid var(--c-border) !important;
        border-radius: 12px !important;
    }
    [data-testid="stExpander"] summary {
        color: var(--c-text-primary) !important;
    }

    /* Form container */
    [data-testid="stForm"] {
        border: 1.5px solid var(--c-border) !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* Number input */
    .stNumberInput input:focus,
    .stTextInput input:focus {
        border-color: var(--c-ok-strip) !important;
        box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15) !important;
    }

    /* Caption / small */
    .stCaption {
        color: var(--c-text-muted) !important;
    }

    /* Divider */
    hr {
        border-color: var(--c-border-div) !important;
        opacity: 1 !important;
    }

    /* Alert native */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
    }
    [data-testid="stAlert"][data-baseweb="notification"] {
        background-color: var(--c-ok-box-bg) !important;
        border-color: var(--c-ok-strip) !important;
        color: var(--c-ok-text) !important;
    }

    /* Dataframe / table */
    [data-testid="stDataFrame"] {
        background-color: var(--c-card) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    [data-testid="stDataFrame"] table {
        color: var(--c-text-primary) !important;
    }
    [data-testid="stDataFrame"] th {
        background-color: var(--c-st-secondary) !important;
        color: var(--c-text-muted) !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
    }
    [data-testid="stDataFrame"] td {
        color: var(--c-text-primary) !important;
        font-size: 13px !important;
    }

    /* Line chart */
    [data-testid="stArrowVegaLiteChart"] {
        background-color: var(--c-card) !important;
        border: 1.5px solid var(--c-border) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* ── METRIC CARD ── */
    .metric-card {
        background: var(--c-card);
        border: 1.5px solid var(--c-border);
        border-radius: 16px;
        padding: 18px 20px 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: box-shadow 0.2s;
    }
    .metric-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.10); }
    .metric-card.alert {
        border: 2px solid var(--c-border-alert);
        background: var(--c-card-alert);
        box-shadow: 0 2px 12px rgba(239,68,68,0.10);
    }
    .metric-card .metric-label {
        font-size: 11px; font-weight: 700; letter-spacing: 0.07em;
        color: var(--c-text-muted); margin-bottom: 8px;
    }
    .metric-card .metric-value {
        font-size: 34px; font-weight: 700;
        color: var(--c-text-primary); line-height: 1.1;
    }
    .metric-card .metric-unit {
        font-size: 15px; font-weight: 400;
        color: var(--c-text-muted); margin-left: 3px;
    }
    .metric-card .metric-ideal {
        font-size: 11px; color: var(--c-text-muted); margin-top: 3px;
    }

    /* ── BADGE ── */
    .badge {
        display: inline-block; padding: 4px 13px;
        border-radius: 20px; font-size: 12px; font-weight: 600;
        letter-spacing: 0.02em;
    }
    .badge-ok     { background: var(--c-ok-bg);     color: var(--c-ok-text); }
    .badge-warn   { background: var(--c-warn-bg);   color: var(--c-warn-text); }
    .badge-danger { background: var(--c-danger-bg); color: var(--c-danger-text); }

    /* ── ALERT BOX ── */
    .alert-box {
        background: var(--c-danger-box);
        border-left: 4px solid var(--c-danger-strip);
        border-radius: 0 10px 10px 0;
        padding: 14px 18px; margin-bottom: 10px;
    }
    .alert-box strong { color: var(--c-danger-text); font-size: 14px; }
    .alert-box span   { color: var(--c-danger-text); font-size: 13px; opacity: 0.85; }

    /* ── OK BOX ── */
    .ok-box {
        background: var(--c-ok-box-bg);
        border-left: 4px solid var(--c-ok-strip);
        border-radius: 0 10px 10px 0;
        padding: 14px 18px; margin-bottom: 18px;
        color: var(--c-ok-text); font-size: 14px; font-weight: 500;
    }

    /* ── INFO CARD ── */
    .info-card {
        background: var(--c-info-bg);
        border: 1.5px solid var(--c-info-border);
        border-radius: 14px; padding: 16px 18px;
        margin-bottom: 6px; color: var(--c-info-text) !important;
    }
    .info-card small { color: var(--c-info-small) !important; font-size: 13px; }
    .info-card .rentang-label {
        font-size: 13px; font-weight: 700;
        color: var(--c-info-text) !important;
        margin-bottom: 10px; display: block; letter-spacing: 0.02em;
    }
    .info-card .rentang-item {
        display: inline-block;
        background: var(--c-info-chip);
        border: 1.5px solid var(--c-info-border);
        border-radius: 8px; padding: 6px 13px;
        margin: 4px 4px 0 0; font-size: 13px;
        color: var(--c-info-text) !important; font-weight: 600;
    }

    /* ── PREDIKSI CARD ── */
    .prediksi-card {
        background: var(--c-blue-bg);
        border: 1.5px solid var(--c-blue-border);
        border-radius: 14px; padding: 18px 20px; margin-bottom: 6px;
    }
    .prediksi-card .pred-title {
        font-size: 14px; font-weight: 700;
        color: var(--c-blue-text); margin-bottom: 12px;
        display: block; letter-spacing: 0.01em;
    }
    .pred-item {
        display: inline-flex; flex-direction: column;
        background: var(--c-blue-card);
        border: 1.5px solid var(--c-blue-border);
        border-radius: 12px; padding: 12px 16px;
        margin: 4px 6px 4px 0; min-width: 150px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .pred-item .pred-label {
        font-size: 11px; color: var(--c-blue-label);
        font-weight: 600; letter-spacing: 0.04em; margin-bottom: 5px;
    }
    .pred-item .pred-val {
        font-size: 22px; font-weight: 700;
        color: var(--c-blue-val); line-height: 1.2;
    }
    .pred-item .pred-unit { font-size: 13px; color: var(--c-blue-unit); margin-left: 2px; }
    .pred-item .pred-status { font-size: 12px; margin-top: 5px; font-weight: 600; }
    .pred-warn   { color: var(--c-pred-warn) !important; }
    .pred-danger { color: var(--c-pred-danger) !important; }
    .pred-ok     { color: var(--c-pred-ok) !important; }
    .pred-note   { font-size: 11px; color: var(--c-blue-note); margin-top: 12px; font-style: italic; }

    /* ── GAUGE ── */
    .gauge-container {
        position: relative; height: 8px;
        background: var(--c-gauge-bg);
        border-radius: 8px; margin: 10px 0 4px; overflow: visible;
    }
    .gauge-ideal {
        position: absolute; height: 100%;
        background: linear-gradient(90deg, var(--c-ok-border), var(--c-ok-strip));
        border-radius: 8px;
    }
    .gauge-thumb {
        position: absolute; top: -4px; width: 16px; height: 16px;
        border-radius: 50%; border: 2.5px solid var(--c-gauge-thumb);
        transform: translateX(-50%); box-shadow: 0 1px 4px rgba(0,0,0,0.22);
    }

    /* ── KONTROL GRUP ── */
    .ctrl-group {
        background: var(--c-ctrl-bg);
        border: 1.5px solid var(--c-ctrl-border);
        border-radius: 14px; padding: 14px 16px 10px;
        height: 100%; box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .ctrl-group-title {
        font-size: 11px; font-weight: 700; letter-spacing: 0.07em;
        color: var(--c-ctrl-title); margin-bottom: 10px;
        padding-bottom: 8px; border-bottom: 1.5px solid var(--c-ctrl-divider);
    }

    /* ── TOMBOL ── */
    .stButton>button {
        border-radius: 9px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important; font-size: 13px !important;
        transition: all 0.15s !important;
        background-color: var(--c-card) !important;
        color: var(--c-text-primary) !important;
        border: 1.5px solid var(--c-border-muted) !important;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--c-ok-strip) !important;
        color: #fff !important;
        border-color: var(--c-ok-strip) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: var(--c-ok-border) !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
        border-color: var(--c-ok-strip) !important;
    }

    /* ── DATAFRAME ── */
    .dataframe { border-radius: 10px !important; overflow: hidden; }

    div[data-testid="stHorizontalBlock"] { gap: 14px; }
</style>
""", unsafe_allow_html=True)


# =========================
# DATA TANAMAN GREENHOUSE
# =========================

TANAMAN_GREENHOUSE = {
    "🍅 Tomat": {
        "deskripsi": "Solanum lycopersicum — butuh suhu hangat & kelembaban sedang",
        "kelembaban_tanah": (60, 80),
        "suhu":             (20, 27),
        "kelembaban_udara": (60, 80),
        "ph_tanah":         (6.0, 6.8),
        "sensor_default":   {"kelembaban_tanah": 68.0, "suhu": 24.0, "kelembaban_udara": 70.0, "ph_tanah": 6.3},
    },
    "🌶️ Cabai": {
        "deskripsi": "Capsicum annuum — menyukai suhu hangat & kelembaban rendah–sedang",
        "kelembaban_tanah": (50, 70),
        "suhu":             (22, 30),
        "kelembaban_udara": (50, 70),
        "ph_tanah":         (6.0, 6.8),
        "sensor_default":   {"kelembaban_tanah": 60.0, "suhu": 26.0, "kelembaban_udara": 60.0, "ph_tanah": 6.4},
    },
    "🥒 Mentimun": {
        "deskripsi": "Cucumis sativus — tumbuh baik di suhu hangat & kelembaban tinggi",
        "kelembaban_tanah": (65, 85),
        "suhu":             (22, 28),
        "kelembaban_udara": (70, 90),
        "ph_tanah":         (6.0, 7.0),
        "sensor_default":   {"kelembaban_tanah": 72.0, "suhu": 25.0, "kelembaban_udara": 78.0, "ph_tanah": 6.5},
    },
    "🥬 Selada": {
        "deskripsi": "Lactuca sativa — cocok suhu sejuk & kelembaban tinggi",
        "kelembaban_tanah": (60, 75),
        "suhu":             (15, 22),
        "kelembaban_udara": (60, 80),
        "ph_tanah":         (6.0, 7.0),
        "sensor_default":   {"kelembaban_tanah": 65.0, "suhu": 18.0, "kelembaban_udara": 68.0, "ph_tanah": 6.5},
    },
    "🌿 Bayam": {
        "deskripsi": "Amaranthus — tahan panas, butuh kelembaban sedang",
        "kelembaban_tanah": (50, 70),
        "suhu":             (18, 30),
        "kelembaban_udara": (55, 75),
        "ph_tanah":         (6.0, 7.0),
        "sensor_default":   {"kelembaban_tanah": 60.0, "suhu": 24.0, "kelembaban_udara": 65.0, "ph_tanah": 6.5},
    },
    "🍓 Stroberi": {
        "deskripsi": "Fragaria × ananassa — suhu sejuk, tanah lembab, drainase baik",
        "kelembaban_tanah": (60, 75),
        "suhu":             (15, 22),
        "kelembaban_udara": (60, 75),
        "ph_tanah":         (5.5, 6.5),
        "sensor_default":   {"kelembaban_tanah": 67.0, "suhu": 18.0, "kelembaban_udara": 68.0, "ph_tanah": 6.0},
    },
    "🌸 Anggrek": {
        "deskripsi": "Orchidaceae — kelembaban udara tinggi, suhu hangat–sejuk",
        "kelembaban_tanah": (40, 60),
        "suhu":             (18, 27),
        "kelembaban_udara": (60, 80),
        "ph_tanah":         (5.5, 6.5),
        "sensor_default":   {"kelembaban_tanah": 50.0, "suhu": 22.0, "kelembaban_udara": 70.0, "ph_tanah": 6.0},
    },
    "🌱 Kangkung Hidroponik": {
        "deskripsi": "Ipomoea aquatica — tumbuh cepat, kelembaban tinggi, pH netral",
        "kelembaban_tanah": (70, 90),
        "suhu":             (20, 30),
        "kelembaban_udara": (65, 85),
        "ph_tanah":         (6.0, 7.0),
        "sensor_default":   {"kelembaban_tanah": 80.0, "suhu": 25.0, "kelembaban_udara": 75.0, "ph_tanah": 6.5},
    },
}

LABELS = {
    "kelembaban_tanah": "💧 Kelembaban Tanah",
    "suhu":             "🌡️ Suhu",
    "kelembaban_udara": "💨 Kelembaban Udara",
    "ph_tanah":         "🧪 pH Tanah",
}
UNITS = {"kelembaban_tanah": "%", "suhu": "°C", "kelembaban_udara": "%", "ph_tanah": ""}

SENSOR_RANGE = {
    "kelembaban_tanah": (0,   100),
    "suhu":             (10,  45),
    "kelembaban_udara": (20,  100),
    "ph_tanah":         (4.0, 9.0),
}


# =========================
# FUNGSI BANTU
# =========================

def ideal_tanaman(tanaman):
    t = TANAMAN_GREENHOUSE[tanaman]
    return {k: t[k] for k in ["kelembaban_tanah", "suhu", "kelembaban_udara", "ph_tanah"]}


def analisa(nilai, jenis, tanaman):
    lo, hi = ideal_tanaman(tanaman)[jenis]
    if nilai < lo:
        label_rendah = {
            "kelembaban_tanah": "Terlalu Kering",
            "suhu":             "Terlalu Dingin",
            "kelembaban_udara": "Kelembaban Udara Rendah",
            "ph_tanah":         "Terlalu Asam",
        }
        return label_rendah[jenis]
    if nilai <= hi:
        return "Optimal"
    label_tinggi = {
        "kelembaban_tanah": "Terlalu Basah",
        "suhu":             "Terlalu Panas",
        "kelembaban_udara": "Kelembaban Udara Tinggi",
        "ph_tanah":         "Terlalu Basa",
    }
    return label_tinggi[jenis]


def saran(status, jenis):
    SARAN = {
        "kelembaban_tanah": {
            "Terlalu Kering": "Segera nyalakan sistem irigasi / pompa air greenhouse.",
            "Optimal":        "Kelembaban tanah dalam kondisi optimal untuk tanaman ini.",
            "Terlalu Basah":  "Kurangi penyiraman dan periksa drainase pot/media tanam.",
        },
        "suhu": {
            "Terlalu Dingin": "Nyalakan pemanas greenhouse atau tambahkan insulasi plastik.",
            "Optimal":        "Suhu greenhouse ideal untuk pertumbuhan tanaman.",
            "Terlalu Panas":  "Buka ventilasi atap, nyalakan kipas exhaust, atau pasang shading net.",
        },
        "kelembaban_udara": {
            "Kelembaban Udara Rendah": "Aktifkan misting system atau semprot embun secara manual.",
            "Optimal":                 "Kelembaban udara dalam kisaran aman.",
            "Kelembaban Udara Tinggi": "Buka ventilasi samping dan nyalakan kipas sirkulasi.",
        },
        "ph_tanah": {
            "Terlalu Asam": "Tambahkan kapur pertanian (CaCO₃) atau dolomit untuk menaikkan pH.",
            "Optimal":      "pH tanah/media tanam sudah sesuai untuk tanaman ini.",
            "Terlalu Basa": "Tambahkan sulfur atau larutan asam humat untuk menurunkan pH.",
        },
    }
    return SARAN[jenis].get(status, "-")


def is_alert(status):
    return status != "Optimal"


def prediksi_hari_berikutnya(history):
    if len(history) < 3:
        return None
    df = pd.DataFrame(history[::-1])
    col_map = {
        "kelembaban_tanah": "Kelembaban Tanah (%)",
        "suhu":             "Suhu (°C)",
        "kelembaban_udara": "Kelembaban Udara (%)",
        "ph_tanah":         "pH Tanah",
    }
    hasil = {}
    n = len(df)
    x = np.arange(n)
    for key, col in col_map.items():
        y = df[col].values.astype(float)
        a, b = np.polyfit(x, y, 1)
        pred = a * n + b
        lo, hi = SENSOR_RANGE[key]
        pred = round(float(np.clip(pred, lo, hi)), 1)
        hasil[key] = pred
    return hasil


def badge_class(status):
    if status == "Optimal":
        return "badge-ok"
    if status in ["Terlalu Kering", "Terlalu Dingin", "Kelembaban Udara Rendah", "Terlalu Asam"]:
        return "badge-warn"
    return "badge-danger"


def gauge_html(nilai, jenis, tanaman):
    lo, hi = ideal_tanaman(tanaman)[jenis]
    v_min, v_max = SENSOR_RANGE[jenis]
    span = v_max - v_min
    ideal_left  = ((lo - v_min) / span) * 100
    ideal_width = ((hi - lo)    / span) * 100
    thumb_left  = max(0, min(100, ((nilai - v_min) / span) * 100))
    ok = lo <= nilai <= hi
    color = "#3B6D11" if ok else "#E24B4A"
    return (
        f"<div class='gauge-container'>"
        f"<div class='gauge-ideal' style='left:{ideal_left:.1f}%;width:{ideal_width:.1f}%'></div>"
        f"<div class='gauge-thumb' style='left:{thumb_left:.1f}%;background:{color}'></div>"
        f"</div>"
    )


# =========================
# SESSION STATE
# =========================

def init_state():
    defaults = {
        "phase":   "onboarding",
        "tanaman": "",
        "hari":    1,
        "sensors": {},
        "history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# =========================
# FASE ONBOARDING
# =========================

if st.session_state.phase == "onboarding":

    _, col_center, _ = st.columns([1, 2.2, 1])
    with col_center:
        st.markdown("## 🏡 Pantau Tani — Greenhouse")
        st.markdown(
            "Sistem monitoring lingkungan greenhouse berbasis IoT. "
            "Pilih tanaman yang dibudidayakan — rentang ideal sensor akan menyesuaikan otomatis."
        )
        st.markdown("---")

        st.markdown("#### 🌿 Pilih Tanaman Greenhouse")
        tanaman_list = list(TANAMAN_GREENHOUSE.keys())
        cols_per_row = 4
        for row_start in range(0, len(tanaman_list), cols_per_row):
            row_items = tanaman_list[row_start:row_start + cols_per_row]
            btn_cols = st.columns(len(row_items))
            for col, opt in zip(btn_cols, row_items):
                with col:
                    selected = st.session_state.tanaman == opt
                    label = f"**{opt}**" if selected else opt
                    if st.button(label, key=f"t_{opt}", use_container_width=True):
                        st.session_state.tanaman = opt
                        st.session_state.sensors = dict(TANAMAN_GREENHOUSE[opt]["sensor_default"])
                        st.rerun()

        if st.session_state.tanaman:
            t = st.session_state.tanaman
            info = TANAMAN_GREENHOUSE[t]
            ideal = ideal_tanaman(t)
            st.success(f"✅ Tanaman dipilih: **{t}**")
            st.markdown(
                f"<div class='info-card'>"
                f"<small>{info['deskripsi']}</small><br><br>"
                f"<span class='rentang-label'>📊 Rentang Ideal Sensor</span>"
                f"<span class='rentang-item'>💧 Kelembaban Tanah: {ideal['kelembaban_tanah'][0]}–{ideal['kelembaban_tanah'][1]}%</span>"
                f"<span class='rentang-item'>🌡️ Suhu: {ideal['suhu'][0]}–{ideal['suhu'][1]}°C</span>"
                f"<span class='rentang-item'>💨 Kelembaban Udara: {ideal['kelembaban_udara'][0]}–{ideal['kelembaban_udara'][1]}%</span>"
                f"<span class='rentang-item'>🧪 pH: {ideal['ph_tanah'][0]}–{ideal['ph_tanah'][1]}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Pilih jenis tanaman greenhouse terlebih dahulu.")

        st.markdown("---")

        if st.session_state.tanaman:
            st.markdown("#### 📡 Input Kondisi Awal Sensor IoT")
            s = st.session_state.sensors
            t = st.session_state.tanaman
            ideal = ideal_tanaman(t)

            c1, c2 = st.columns(2)
            with c1:
                s["kelembaban_tanah"] = st.slider(
                    "💧 Kelembaban Tanah (%)", 0, 100, int(s["kelembaban_tanah"]), 1
                )
                st.caption(f"Ideal untuk {t}: {ideal['kelembaban_tanah'][0]}–{ideal['kelembaban_tanah'][1]}%")
                s["suhu"] = st.number_input(
                    "🌡️ Suhu Greenhouse (°C)", 10.0, 45.0, float(s["suhu"]), 0.1, format="%.1f"
                )
                st.caption(f"Ideal untuk {t}: {ideal['suhu'][0]}–{ideal['suhu'][1]}°C")
            with c2:
                s["kelembaban_udara"] = st.slider(
                    "💨 Kelembaban Udara (%)", 20, 100, int(s["kelembaban_udara"]), 1
                )
                st.caption(f"Ideal untuk {t}: {ideal['kelembaban_udara'][0]}–{ideal['kelembaban_udara'][1]}%")
                s["ph_tanah"] = st.number_input(
                    "🧪 pH Tanah / Media Tanam", 4.0, 9.0, float(s["ph_tanah"]), 0.1, format="%.1f"
                )
                st.caption(f"Ideal untuk {t}: {ideal['ph_tanah'][0]}–{ideal['ph_tanah'][1]}")

            st.session_state.sensors = s
            st.markdown("---")

            if st.button("🚀 Mulai Monitoring Greenhouse", use_container_width=True, type="primary"):
                entry = {
                    "Hari":                  "Hari 1",
                    "Waktu":                 datetime.now().strftime("%H:%M"),
                    "Kelembaban Tanah (%)":  s["kelembaban_tanah"],
                    "Suhu (°C)":             s["suhu"],
                    "Kelembaban Udara (%)":  s["kelembaban_udara"],
                    "pH Tanah":              s["ph_tanah"],
                }
                st.session_state.history = [entry]
                st.session_state.hari    = 1
                st.session_state.phase   = "dashboard"
                st.rerun()


# =========================
# FASE DASHBOARD
# =========================

else:
    s       = st.session_state.sensors
    tanaman = st.session_state.tanaman
    ideal   = ideal_tanaman(tanaman)

    statuses = {k: analisa(s[k], k, tanaman) for k in s}
    alerts   = {k: statuses[k] for k in statuses if is_alert(statuses[k])}

    # --- Header ---
    h1, h2 = st.columns([3, 2])
    with h1:
        alert_badge = (
            f" &nbsp;<span class='badge badge-danger'>⚠️ {len(alerts)} Peringatan</span>"
            if alerts else ""
        )
        st.markdown(
            f"<h2 style='margin:0;color:var(--c-text-primary)'>🏡 Pantau Tani Greenhouse &nbsp;"
            f"<span class='badge badge-ok'>{tanaman}</span>"
            f"{alert_badge}</h2>"
            f"<p style='color:var(--c-text-muted);margin:5px 0 0;font-size:13px'>"
            f"Hari ke-{st.session_state.hari} monitoring &nbsp;·&nbsp; "
            f"Update: {datetime.now().strftime('%H:%M:%S')}</p>",
            unsafe_allow_html=True
        )
    with h2:
        ca, cb = st.columns(2)
        with ca:
            if st.button("✏️ Ganti Tanaman", use_container_width=True):
                st.session_state.phase = "onboarding"
                st.rerun()
        with cb:
            if st.button("📥 Perbarui Data Sensor", use_container_width=True, type="primary"):
                st.session_state.show_update_form = True

    st.markdown("---")

    # --- Form Perbarui Data Sensor ---
    if st.session_state.get("show_update_form", False):
        with st.form("form_update_sensor"):
            st.markdown("#### 📡 Input Data Sensor Terbaru")
            f1, f2 = st.columns(2)
            with f1:
                new_kt = st.slider("💧 Kelembaban Tanah (%)", 0, 100, int(s["kelembaban_tanah"]), 1)
                st.caption(f"Ideal: {ideal['kelembaban_tanah'][0]}–{ideal['kelembaban_tanah'][1]}%")
                new_su = st.number_input("🌡️ Suhu (°C)", 10.0, 45.0, float(s["suhu"]), 0.1, format="%.1f")
                st.caption(f"Ideal: {ideal['suhu'][0]}–{ideal['suhu'][1]}°C")
            with f2:
                new_ku = st.slider("💨 Kelembaban Udara (%)", 20, 100, int(s["kelembaban_udara"]), 1)
                st.caption(f"Ideal: {ideal['kelembaban_udara'][0]}–{ideal['kelembaban_udara'][1]}%")
                new_ph = st.number_input("🧪 pH Tanah", 4.0, 9.0, float(s["ph_tanah"]), 0.1, format="%.1f")
                st.caption(f"Ideal: {ideal['ph_tanah'][0]}–{ideal['ph_tanah'][1]}")
            sc1, sc2 = st.columns(2)
            with sc1:
                submitted = st.form_submit_button("✅ Simpan & Perbarui", use_container_width=True, type="primary")
            with sc2:
                cancelled = st.form_submit_button("❌ Batal", use_container_width=True)

        if submitted:
            new_s = {
                "kelembaban_tanah": float(new_kt),
                "suhu":             float(new_su),
                "kelembaban_udara": float(new_ku),
                "ph_tanah":         float(new_ph),
            }
            st.session_state.sensors = new_s
            st.session_state.hari   += 1
            entry = {
                "Hari":                 f"Hari {st.session_state.hari}",
                "Waktu":                datetime.now().strftime("%H:%M"),
                "Kelembaban Tanah (%)": new_s["kelembaban_tanah"],
                "Suhu (°C)":            new_s["suhu"],
                "Kelembaban Udara (%)": new_s["kelembaban_udara"],
                "pH Tanah":             new_s["ph_tanah"],
            }
            st.session_state.history.insert(0, entry)
            st.session_state.history = st.session_state.history[:30]
            st.session_state.show_update_form = False
            st.rerun()
        if cancelled:
            st.session_state.show_update_form = False
            st.rerun()

        st.markdown("---")

    # --- Panel Peringatan ---
    if alerts:
        for k, status in alerts.items():
            st.markdown(
                f"<div class='alert-box'>"
                f"<strong>⚠️ {LABELS[k]} — {status}</strong><br>"
                f"<span style='color:var(--c-danger-text)'>{saran(status, k)}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div class='ok-box'>✅ <strong>Semua kondisi greenhouse optimal.</strong> "
            "Tidak ada tindakan yang diperlukan.</div>",
            unsafe_allow_html=True
        )

    # --- Panel Prediksi ---
    prediksi = prediksi_hari_berikutnya(st.session_state.history)
    if prediksi:
        hari_pred = st.session_state.hari + 1
        pred_items_html = ""
        for k in ["kelembaban_tanah", "suhu", "kelembaban_udara", "ph_tanah"]:
            val = prediksi[k]
            val_str = f"{val:.1f}" if val % 1 != 0 else str(int(val))
            status_pred = analisa(val, k, tanaman)
            if status_pred == "Optimal":
                sc = "pred-ok"; icon = "✅"
            elif status_pred in ["Terlalu Kering","Terlalu Dingin","Kelembaban Udara Rendah","Terlalu Asam"]:
                sc = "pred-warn"; icon = "⚠️"
            else:
                sc = "pred-danger"; icon = "🔴"
            pred_items_html += (
                f"<div class='pred-item'>"
                f"<span class='pred-label'>{LABELS[k]}</span>"
                f"<span><span class='pred-val'>{val_str}</span>"
                f"<span class='pred-unit'> {UNITS[k]}</span></span>"
                f"<span class='pred-status {sc}'>{icon} {status_pred}</span>"
                f"</div>"
            )
        n_data = len(st.session_state.history)
        st.markdown(
            f"<div class='prediksi-card'>"
            f"<span class='pred-title'>🔮 Prediksi Kondisi Hari ke-{hari_pred} (Linear Regression · {n_data} data)</span>"
            f"{pred_items_html}"
            f"<div class='pred-note'>* Prediksi dihitung dari tren {n_data} data historis. "
            f"Semakin banyak data, semakin akurat prediksi.</div>"
            f"</div>",
            unsafe_allow_html=True
        )
    elif len(st.session_state.history) < 3:
        sisa = 3 - len(st.session_state.history)
        st.markdown(
            f"<div style='background:var(--c-blue-bg);border:1.5px solid var(--c-blue-border);"
            f"border-radius:12px;padding:14px 18px;margin-bottom:14px;"
            f"color:var(--c-blue-text);font-size:13px;font-weight:500'>"
            f"🔮 Prediksi akan tersedia setelah <b>{sisa} data lagi</b> diinput "
            f"(minimal 3 hari diperlukan untuk Linear Regression)."
            f"</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # --- Kartu Metrik ---
    keys = ["kelembaban_tanah", "suhu", "kelembaban_udara", "ph_tanah"]
    cols = st.columns(4)
    for col, k in zip(cols, keys):
        with col:
            status    = statuses[k]
            alert_cls = "alert" if is_alert(status) else ""
            val       = s[k]
            val_str   = f"{val:.1f}" if isinstance(val, float) and val % 1 != 0 else str(val)
            lo, hi    = ideal[k]
            st.markdown(
                f"<div class='metric-card {alert_cls}'>"
                f"<div class='metric-label'>{LABELS[k].upper()}</div>"
                f"<div><span class='metric-value'>{val_str}</span>"
                f"<span class='metric-unit'>{UNITS[k]}</span></div>"
                f"{gauge_html(val, k, tanaman)}"
                f"<div class='metric-ideal'>Ideal: {lo}–{hi}{UNITS[k]}</div>"
                f"<div style='margin-top:8px'><span class='badge {badge_class(status)}'>{status}</span></div>"
                f"</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

    # --- Ringkasan & Rekomendasi ---
    with st.expander("📋 Ringkasan & Rekomendasi Lengkap", expanded=True):
        r1, r2 = st.columns(2)
        for i, k in enumerate(keys):
            col = r1 if i < 2 else r2
            with col:
                status = statuses[k]
                bc = badge_class(status)
                lo, hi = ideal[k]
                st.markdown(
                    f"**{LABELS[k]}** &nbsp;<span class='badge {bc}'>{status}</span><br>"
                    f"<small style='color:var(--c-text-muted)'>Ideal {tanaman}: {lo}–{hi}{UNITS[k]}</small><br>"
                    f"<small style='color:var(--c-text-secondary)'>{saran(status, k)}</small>",
                    unsafe_allow_html=True
                )
                st.markdown("<br>", unsafe_allow_html=True)

    # --- Kontrol Manual Greenhouse ---
    st.subheader("🎮 Kontrol Manual Perangkat Greenhouse")
    kc1, kc2, kc3, kc4 = st.columns(4)

    with kc1:
        st.markdown("<div class='ctrl-group'><div class='ctrl-group-title'>💧 KELEMBABAN TANAH</div></div>",
                    unsafe_allow_html=True)
        if st.button("▶ Nyalakan Pompa Irigasi", key="k1", use_container_width=True, type="primary"):
            st.success("✅ Pompa irigasi dihidupkan.")
        if st.button("⏹ Matikan Pompa Irigasi", key="k2", use_container_width=True):
            st.info("⏹ Pompa irigasi dimatikan.")
        if st.button("💧 Aktifkan Drip Irrigation", key="k3", use_container_width=True):
            st.success("✅ Drip irrigation diaktifkan.")

    with kc2:
        st.markdown("<div class='ctrl-group'><div class='ctrl-group-title'>🌡️ SUHU</div></div>",
                    unsafe_allow_html=True)
        if st.button("❄️ Nyalakan Kipas Exhaust", key="s1", use_container_width=True):
            st.success("✅ Kipas exhaust dihidupkan untuk menurunkan suhu.")
        if st.button("🔥 Nyalakan Pemanas", key="s2", use_container_width=True, type="primary"):
            st.success("✅ Pemanas greenhouse dinyalakan.")
        if st.button("🪟 Buka Ventilasi Atap", key="s3", use_container_width=True):
            st.success("✅ Ventilasi atap dibuka.")
        if st.button("🌿 Aktifkan Shading Net", key="s4", use_container_width=True):
            st.success("✅ Shading net diaktifkan.")

    with kc3:
        st.markdown("<div class='ctrl-group'><div class='ctrl-group-title'>💨 KELEMBABAN UDARA</div></div>",
                    unsafe_allow_html=True)
        if st.button("🌫️ Nyalakan Misting System", key="u1", use_container_width=True, type="primary"):
            st.success("✅ Misting system diaktifkan.")
        if st.button("💨 Nyalakan Humidifier", key="u2", use_container_width=True):
            st.success("✅ Humidifier dinyalakan.")
        if st.button("🔄 Nyalakan Kipas Sirkulasi", key="u3", use_container_width=True):
            st.success("✅ Kipas sirkulasi dihidupkan untuk mengurangi kelembaban.")

    with kc4:
        st.markdown("<div class='ctrl-group'><div class='ctrl-group-title'>🧪 pH TANAH</div></div>",
                    unsafe_allow_html=True)
        if st.button("⬆ Pompa Larutan Kapur", key="p1", use_container_width=True):
            st.success("✅ Pompa larutan kapur (CaCO₃) diaktifkan — pH akan naik.")
        if st.button("⬇ Pompa Larutan Asam", key="p2", use_container_width=True):
            st.success("✅ Pompa larutan asam humat diaktifkan — pH akan turun.")
        if st.button("🧪 Aktifkan Dosis Pupuk", key="p3", use_container_width=True, type="primary"):
            st.success("✅ Sistem dosing pupuk diaktifkan.")

    # --- Riwayat ---
    if st.session_state.history:
        st.markdown("---")
        st.subheader(f"📈 Riwayat Monitoring ({len(st.session_state.history)} Hari Terakhir)")
        df = pd.DataFrame(st.session_state.history)

        def style_row(row):
            result = []
            k_map = {
                "Kelembaban Tanah (%)": "kelembaban_tanah",
                "Suhu (°C)":            "suhu",
                "Kelembaban Udara (%)": "kelembaban_udara",
                "pH Tanah":             "ph_tanah",
            }
            for col_name in row.index:
                style = ""
                if col_name in k_map:
                    st_val = analisa(row[col_name], k_map[col_name], tanaman)
                    # Gunakan warna dengan kontras baik di kedua tema:
                    # merah/hijau medium — cukup terang di dark, cukup jenuh di light
                    style = (
                        "background-color:rgba(239,68,68,0.15);color:#B91C1C;font-weight:600"
                        if is_alert(st_val)
                        else "background-color:rgba(34,197,94,0.13);color:#15803D;font-weight:600"
                    )
                result.append(style)
            return result

        styled = df.style.apply(style_row, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # --- Grafik Tren ---
    if len(st.session_state.history) > 1:
        st.subheader("📉 Tren Sensor Greenhouse")
        df_chart = pd.DataFrame(st.session_state.history[::-1]).set_index("Hari")
        tab1, tab2, tab3, tab4 = st.tabs([
            "💧 Kelembaban Tanah", "🌡️ Suhu", "💨 Kelembaban Udara", "🧪 pH"
        ])
        with tab1:
            st.line_chart(df_chart[["Kelembaban Tanah (%)"]])
        with tab2:
            st.line_chart(df_chart[["Suhu (°C)"]])
        with tab3:
            st.line_chart(df_chart[["Kelembaban Udara (%)"]])
        with tab4:
            st.line_chart(df_chart[["pH Tanah"]])

    st.markdown("---")
    st.caption("🏡 Pantau Tani Greenhouse — Sistem Monitoring Pertanian Cerdas · Python & Streamlit")