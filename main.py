import streamlit as st
import pandas as pd
import time
from gamedata import NW_CODES # 匯入剛剛建立的資料

# --- 1. 遊戲初始化 ---
if 'project_status' not in st.session_state:
    st.session_state.project_status = {
        "step": "Project_Setup", # 當前階段：Setup -> Paperless -> Inspection
        "inventory": [],         # 玩家擁有的文件
        "uploaded_files": {},    # 已上傳到建管處的文件
        "params": {}             # 基地參數 (面積、造價等)
    }

# --- 2. 介面路由 (Router) ---
def main():
    st.set_page_config(page_title="跑照大作戰", layout="wide")
    
    status = st.session_state.project_status["step"]
    
    if status == "Project_Setup":
        render_setup_page()
    elif status == "Paperless_System":
        render_paperless_page()
    elif status == "Site_Inspection":
        render_site_page()

# --- 3. 各階段頁面函式 ---

def render_setup_page():
    st.title("📋 新建案：基本資料輸入")
    
    with st.form("setup_form"):
        area = st.number_input("基地面積 (m2)", min_value=0)
        duration = st.number_input("預計工期 (月)", min_value=0)
        is_demolition = st.checkbox("包含拆除工程 (拆併建)")
        road_width = st.number_input("臨路寬度 (m)", min_value=0)
        
        if st.form_submit_button("建立專案"):
            # 儲存參數
            st.session_state.project_status["params"] = {
                "area": area,
                "duration": duration,
                "is_demolition": is_demolition,
                "road_width": road_width
            }
            # 觸發邏輯判定 (例如：是否需逕流廢水)
            if area * duration >= 4600:
                st.toast("⚠️ 觸發高難度副本：逕流廢水削減計畫！", icon="🚨")
            
            st.session_state.project_status["step"] = "Paperless_System"
            st.rerun()

def render_paperless_page():
    st.title("💻 台北市無紙化上傳系統")
    
    # 模擬左側：文件暫存區
    with st.sidebar:
        st.header("📂 你的文件包")
        # 這裡可以做成按鈕，讓玩家「製作」文件
        if st.button("製作：施工計畫書"):
            st.session_state.project_status["inventory"].append("NW3300")
            st.success("已獲得 NW3300！")

    # 模擬中間：上傳區
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("請將檔案拖曳至下方，並確認編碼正確。")
        uploaded = st.file_uploader("建管處傳送門", accept_multiple_files=True)
        
        if uploaded and st.button("送出電子簽章"):
            # 檢查邏輯
            errors = []
            for file in uploaded:
                # 模擬檢查檔名是否包含正確編碼
                valid = False
                for code in NW_CODES:
                    if code in file.name:
                        valid = True
                        break
                if not valid:
                    errors.append(f"❌ 退件：{file.name} 檔名編碼錯誤！")
            
            if errors:
                for e in errors: st.error(e)
            else:
                st.balloons()
                st.success("✅ 掛號成功！進入下一階段...")
                time.sleep(2)
                st.session_state.project_status["step"] = "Site_Inspection"
                st.rerun()

    with col2:
        st.warning("HiCOS 憑證狀態")
        st.markdown("🟢 **已連線：工商憑證**")
        with st.expander("查看編碼表"):
            st.json(NW_CODES)

def render_site_page():
    st.title("🏗️ 現場放樣勘驗")
    st.write("這裡是 3D 工地現場 (想像圖)...")
    # 這裡可以用圖片 + 按鈕來模擬現場佈置
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://placeholder.co/300x200?text=Site+Fence", caption="圍籬")
        if st.button("加裝防溢座"):
            st.write("已安裝防溢座 (高60cm)")
            
    with col2:
        st.image("https://placeholder.co/300x200?text=Personnel", caption="人員大合照")
        if st.button("召喚：工地主任"):
            st.write("工地主任已到場！")

if __name__ == "__main__":
    main()