import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time

# --- Layout Setup ---
st.set_page_config(layout="wide", page_title="Tide Forecast Tool")

st.markdown("""
    <style>
    .main .block-container { padding: 0.5rem 0.5rem !important; max-width: 100% !important; }
    h1 { font-size: 1.5rem !important; margin: 0 !important; }
    .hour-label { font-size: 1.8rem; font-weight: bold; text-align: center; margin-bottom: 5px; border-bottom: 3px solid #005bac; }
    @media print {
        header, .stDeployButton, .stButton, div[data-testid="stNumberInput"], 
        .stInfo, .stSuccess, .stAlert, [data-testid="stForm"], .no-print, footer, [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        div[data-testid="column"] { flex: 1 1 33.3% !important; width: 33.3% !important; padding: 0 1px !important; }
        img { width: 100% !important; height: auto !important; display: block; }
        @page { size: A4 landscape; margin: 0mm; }
        .main { overflow: hidden !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("Tide Current Forecast - 3H")

with st.container():
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 2])
    with c1: yy_val = st.number_input("Year", value=2026)
    with c2: mm_val = st.number_input("Month", value=2, min_value=1, max_value=12)
    with c3: dd_val = st.number_input("Day", value=8, min_value=1, max_value=31)
    with c4: hh_val = st.number_input("Hour", value=15, min_value=0, max_value=23)
    with c5:
        st.write(" ")
        btn = st.button("RUN FORECAST", use_container_width=True)

def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1200,1800")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()),
        options=options
    )

if btn:
    progress_text = st.empty()
    cols = st.columns(3, gap="small")
    
    for i in range(3):
        target_h = (hh_val + i) % 24
        progress_text.text(f"Fetching {target_h:02d}:00 (Step {i+1}/3)...")
        
        driver = create_driver()
        try:
            # 1. パラメータなしの「真っさらな」入力ページを開く
            driver.get("https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/CurrPredCgi_K.cgi?area=01")
            
            # 2. フォームが見つかるまで待機
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.NAME, "yy")))

            # 3. キーボード入力で数字を打ち込む（これが一番確実！）
            def fill(name, val):
                el = driver.find_element(By.NAME, name)
                el.clear()
                el.send_keys(str(val))

            fill("yy", yy_val)
            fill("mm", mm_val)
            fill("dd", dd_val)
            fill("hh", target_h)

            # 4. 推算ボタンをクリック
            submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_btn.click()

            # 5. 画像が生成されるのを待つ
            time.sleep(7) # サーバーが図を作る時間をしっかり確保
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))

            # 6. 画像を撮影
            img_element = driver.find_element(By.TAG_NAME, "img")
            img_bytes = img_element.screenshot_as_png
            
            with cols[i]:
                st.markdown(f'<div class="hour-label">{target_h:02d}:00</div>', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                
        except Exception as e:
            cols[i].error(f"Error at {target_h:02d}:00")
        finally:
            driver.quit()
            
    progress_text.empty()
    st.success("✅ Success! Legend updated. Press Ctrl + P.")
