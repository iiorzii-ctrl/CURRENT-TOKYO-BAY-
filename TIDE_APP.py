import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

st.set_page_config(layout="wide", page_title="Tide Forecast Tool")

# (中略: 前回のCSS設定をそのまま維持)
st.markdown("""
    <style>
    .main .block-container { padding: 0.5rem 0.5rem !important; max-width: 100% !important; }
    h1 { font-size: 1.5rem !important; margin: 0 !important; padding: 0 !important; }
    .hour-label { font-size: 1.6rem; font-weight: bold; text-align: center; margin-bottom: 2px; border-bottom: 3px solid #005bac; }
    @media print {
        header, .stDeployButton, .stButton, div[data-testid="stNumberInput"], 
        .stInfo, .stSuccess, .stAlert, [data-testid="stForm"], .no-print, footer, [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; max-width: 100vw !important; }
        div[data-testid="column"] { flex: 1 1 33.3% !important; width: 33.3% !important; padding: 0 1px !important; }
        img { width: 100% !important; height: auto !important; display: block; }
        @page { size: A4 landscape; margin: 0mm; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("Tide Current Forecast")

with st.container():
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 2])
    with c1: yy = st.number_input("Year", value=2026)
    with c2: mm = st.number_input("Month", value=2, min_value=1, max_value=12)
    with c3: dd = st.number_input("Day", value=8, min_value=1, max_value=31)
    with c4: hh = st.number_input("Hour", value=15, min_value=0, max_value=23)
    with c5:
        st.write(" ")
        btn = st.button("RUN FORECAST", use_container_width=True)

if btn:
    progress = st.empty()
    cols = st.columns(3, gap="small")
    
    # --- 【重要】ここをクラウド（Linux）対応に変更 ---
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1800")
    
    # クラウド環境ではchromiumを利用するように設定
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options
    )
    # ----------------------------------------------

    try:
        for i in range(3):
            target_h = (hh + i) % 24
            progress.text(f"Fetching: {target_h:02d}:00...")
            url = f"https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/CurrPredCgi_K.cgi?area=01&yy={yy}&mm={mm}&dd={dd}&hh={target_h}"
            driver.get(url)
            
            try:
                submit = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                submit.click()
                time.sleep(3) # ネット回線を考慮して少し長めに待機
                
                img_element = driver.find_element(By.TAG_NAME, "img")
                img_bytes = img_element.screenshot_as_png
                
                with cols[i]:
                    st.markdown(f'<div class="hour-label">{target_h:02d}:00</div>', unsafe_allow_html=True)
                    st.image(img_bytes, use_container_width=True)
            except:
                cols[i].error(f"Error: {target_h:02d}:00")
                
        progress.empty()
        st.success("✅ Ready to print! Press Ctrl + P.")
        
    finally:
        driver.quit()