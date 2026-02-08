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
    with c1: yy_val = st.number_input("Year", value=2026)
    with c2: mm_val = st.number_input("Month", value=2, min_value=1, max_value=12)
    with c3: dd_val = st.number_input("Day", value=8, min_value=1, max_value=31)
    with c4: hh_val = st.number_input("Hour", value=15, min_value=0, max_value=23)
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
            target_h = (hh_val + i) % 24
            progress.text(f"Processing: {target_h:02d}:00...")
            
            # 毎回ベースのURLを読み込み直す
            driver.get("https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/CurrPredCgi_K.cgi?area=01")
            
            # 入力ボックスが表示されるまで最大15秒待つ（エラー対策）
            wait = WebDriverWait(driver, 15)
            yy_input = wait.until(EC.presence_of_element_located((By.NAME, "yy")))
            
            # フォームを入力
            yy_input.clear()
            yy_input.send_keys(str(yy_val))
            
            mm_input = driver.find_element(By.NAME, "mm")
            mm_input.clear()
            mm_input.send_keys(str(mm_val))
            
            dd_input = driver.find_element(By.NAME, "dd")
            dd_input.clear()
            dd_input.send_keys(str(dd_val))
            
            hh_input = driver.find_element(By.NAME, "hh")
            hh_input.clear()
            hh_input.send_keys(str(target_h))
            
            # 推算ボタンをクリック
            submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
            submit_btn.click()
            
            # 推算後のページで画像が表示されるまで待つ
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            time.sleep(4) # サーバー側の画像生成完了を確実にするため少し長めに待機
            
            # 画像を撮影
            img_element = driver.find_element(By.TAG_NAME, "img")
            img_bytes = img_element.screenshot_as_png
            
            with cols[i]:
                st.markdown(f'<div class="hour-label">{target_h:02d}:00</div>', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                
        progress.empty()
        st.success("✅ Success! Ready to print.")
        
    except Exception as e:
        st.error(f"Error occurred. Please try again in a few moments.")
        st.write(f"Technical details: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
