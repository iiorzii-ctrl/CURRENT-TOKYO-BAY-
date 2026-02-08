import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

# --- Page Layout ---
st.set_page_config(layout="wide", page_title="Tide Forecast Tool")

st.markdown("""
    <style>
    .main .block-container { padding: 0.5rem 0.5rem !important; max-width: 100% !important; }
    h1 { font-size: 1.5rem !important; margin: 0 !important; padding: 0 !important; }
    .hour-label { font-size: 1.8rem; font-weight: bold; text-align: center; margin-bottom: 5px; border-bottom: 3px solid #005bac; }
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

st.title("Tide Current Forecast - 3H")

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
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1800")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
            options=options
        )

        for i in range(3):
            target_h = (hh + i) % 24
            progress.text(f"Processing: {target_h:02d}:00...")
            
            # 入力画面を読み込む
            driver.get("https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/CurrPredCgi_K.cgi?area=01")
            
            # フォームを直接書き換える（ここが重要！）
            driver.find_element(By.NAME, "yy").clear()
            driver.find_element(By.NAME, "yy").send_keys(str(yy))
            driver.find_element(By.NAME, "mm").clear()
            driver.find_element(By.NAME, "mm").send_keys(str(mm))
            driver.find_element(By.NAME, "dd").clear()
            driver.find_element(By.NAME, "dd").send_keys(str(dd))
            driver.find_element(By.NAME, "hh").clear()
            driver.find_element(By.NAME, "hh").send_keys(str(target_h))
            
            # 推算実行ボタンをクリック
            driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
            time.sleep(3) # 描画待ち
            
            # 画像を撮影
            img_element = driver.find_element(By.TAG_NAME, "img")
            img_bytes = img_element.screenshot_as_png
            
            with cols[i]:
                st.markdown(f'<div class="hour-label">{target_h:02d}:00</div>', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                
        progress.empty()
        st.success("✅ Success! Ready to print.")
        
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
