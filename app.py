import streamlit as st
import time
# 記得要確認您的資料夾中有 gamedata.py 這個檔案，且裡面有 NW_CODES
from gamedata import NW_CODES 

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
    st.set_page_config(page_title="跑照大作戰", layout="wide", page_icon="🏗️")
    
    status = st.session_state.project_status["step"]
    
    # 根據狀態顯示不同頁面
    if status == "Project_Setup":
        render_setup_page()
    elif status == "Paperless_System":
        render_paperless_page()
    elif status == "Site_Inspection":
        render_site_page()

# --- 3. 各階段頁面函式 ---

def render_setup_page():
    st.title("📋 新建案：基本資料輸入")
    st.markdown("請輸入建案的基本參數，系統將自動判斷難度與觸發任務。")
    
    with st.form("setup_form"):
        col1, col2 = st.columns(2)
        with col1:
            area = st.number_input("基地面積 (m2)", min_value=0, value=100)
            duration = st.number_input("預計工期 (月)", min_value=0, value=12)
        with col2:
            road_width = st.number_input("臨路寬度 (m)", min_value=0, value=8)
            is_demolition = st.checkbox("包含拆除工程 (拆併建)")
        
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
                st.toast("⚠️ 警告：觸發高難度副本【逕流廢水削減計畫】！", icon="🚨")
                time.sleep(1)
            
            st.success("專案建立成功！進入無紙化系統...")
            time.sleep(1)
            st.session_state.project_status["step"] = "Paperless_System"
            st.rerun()

def render_paperless_page():
    st.title("💻 台北市無紙化上傳系統")
    
    # 模擬左側：文件暫存區 (背包)
    with st.sidebar:
        st.header("📂 你的文件包")
        st.info("這裡是你目前擁有的文件，請根據右側需求上傳。")
        
        # 這裡模擬玩家透過其他互動獲得文件
        if st.button("製作：施工計畫書 (NW3300)"):
            if "NW3300" not in st.session_state.project_status["inventory"]:
                st.session_state.project_status["inventory"].append("NW3300")
                st.toast("獲得道具：施工計畫書！")
            else:
                st.warning("你已經有這份文件了。")

        st.write("目前擁有：", st.session_state.project_status["inventory"])

    # 模擬中間：上傳區
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("建管處傳送門")
        st.info("請將檔案拖曳至下方，並確認檔名包含正確編碼 (如 NW3300)。")
        
        uploaded = st.file_uploader("選擇檔案上傳", accept_multiple_files=True)
        
        if uploaded and st.button("送出電子簽章"):
            errors = []
            success_count = 0
            
            for file in uploaded:
                # 模擬檢查檔名是否包含正確編碼
                valid = False
                for code in NW_CODES:
                    if code in file.name:
                        valid = True
                        success_count += 1
                        break
                if not valid:
                    errors.append(f"❌ 退件：{file.name} 檔名編碼錯誤或是未知文件！")
            
            if errors:
                for e in errors: st.error(e)
            else:
                if success_count > 0:
                    st.balloons()
                    st.success(f"✅ 掛號成功！共上傳 {success_count} 份文件。進入下一階段...")
                    time.sleep(2)
                    st.session_state.project_status["step"] = "Site_Inspection"
                    st.rerun()
                else:
                    st.warning("請先選擇檔案！")

    # 右側：編碼表與狀態
    with col2:
        st.warning("HiCOS 憑證狀態")
        st.markdown("🟢 **已連線：工商憑證**")
        
        with st.expander("📖 查看 NW 編碼表 (Cheat Sheet)", expanded=True):
            # 將 gamedata 的資料轉為表格顯示，比較好看
            df = []
            for code, data in NW_CODES.items():
                df.append({"代碼": code, "名稱": data["name"]})
            st.dataframe(df, hide_index=True)

def render_site_page():
    st.title("🏗️ 現場放樣勘驗")
    st.markdown("### 目前階段：現場佈置與人員點名")
    
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://placeholder.co/400x300?text=Construction+Site", caption="工地現場模擬圖")
        
        st.subheader("現場設施檢查")
        if st.button("加裝防溢座 (高60cm)"):
            st.success("✅ 已安裝防溢座！符合法規。")
            
    with col2:
        st.subheader("人員大合照 (QTE)")
        st.write("請確保所有人員到齊才能拍照。")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("召喚：工地主任"):
                st.info("工地主任：到！")
        with col_p2:
            if st.button("召喚：專任工程人員"):
                st.info("技師：我來了！")
                
        if st.button("📸 拍攝勘驗合照"):
            st.success("拍攝完成！進入結構體階段 (待續...)")

if __name__ == "__main__":
    main()