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
    /* 通常表示の余白 */
    .main .block-container { padding: 0.5rem 0.5rem !important; max-width: 100% !important; }
    h1 { font-size: 1.5rem !important; margin: 0 !important; }
    .hour-label { font-size: 1.8rem; font-weight: bold; text-align: center; margin-bottom: 5px; border-bottom: 3px solid #005bac; }
    
    /* 印刷用CSS: 余計なものを消し、2ページ目に行かないようにする */
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

# 入力フォーム
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
            progress.text(f"Fetching: {target_h:02d}:00...")
            
            # 【解決策】URLに直接パラメータを詰め込むことで、フォーム入力をスキップします
            direct_url = f"https://www1.kaiho.mlit.go.jp/TIDE/pred2/cgi-bin/CurrPredCgi_K.cgi?area=01&yy={yy_val}&mm={mm_val}&dd={dd_val}&hh={target_h}"
            driver.get(direct_url)
            
            # 画像が表示されるまで最大20秒待機
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            
            # サーバー側での図の生成完了を待つため、少し余裕を持たせます
            time.sleep(4)
            
            # 図の部分を撮影
            img_element = driver.find_element(By.TAG_NAME, "img")
            img_bytes = img_element.screenshot_as_png
            
            with cols[i]:
                st.markdown(f'<div class="hour-label">{target_h:02d}:00</div>', unsafe_allow_html=True)
                st.image(img_bytes, use_container_width=True)
                
        progress.empty()
        st.success("✅ Ready to print! Press Ctrl + P.")
        
    except Exception as e:
        st.error(f"Error occurred. Please wait a moment and try again.")
        st.write(f"Details: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
