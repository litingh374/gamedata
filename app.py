import streamlit as st
import time
from gamedata import NW_CODES 

# --- 1. 遊戲初始化 (Session State) ---
# 這裡設定遊戲開始時的預設狀態
if 'project_status' not in st.session_state:
    st.session_state.project_status = {
        "step": "Project_Setup", # 當前階段：Project_Setup -> Paperless_System -> Site_Inspection
        "params": {}             # 基地參數
    }

# 初始化虛擬檔案系統 (只執行一次)
if "raw_files" not in st.session_state:
    # 這是玩家電腦裡原本有的「亂七八糟原始檔」
    st.session_state.raw_files = [
        "施工計畫書_核定版.docx", 
        "開工申報書_用印掃描.jpg",
        "配筋圖_A3.dwg",
        "圍籬綠美化設計圖.png",
        "工地主任證書_含勞保.pdf",
        "營造業登記證.jpg",
        "這是不相關的自拍照.jpg"
    ]

if "processed_files" not in st.session_state:
    # 這是轉檔好，準備上傳的 PDF
    st.session_state.processed_files = []

# --- 2. 介面路由 (Router) ---
def main():
    st.set_page_config(page_title="跑照大作戰", layout="wide", page_icon="🏗️")
    
    # 讀取目前進度
    status = st.session_state.project_status["step"]
    
    # 根據進度顯示對應的頁面
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
            
            # 觸發邏輯判定
            if area * duration >= 4600:
                st.toast("⚠️ 警告：觸發高難度副本【逕流廢水削減計畫】！", icon="🚨")
                time.sleep(1)
            
            st.success("專案建立成功！進入無紙化系統...")
            time.sleep(1)
            
            # 切換狀態到下一關
            st.session_state.project_status["step"] = "Paperless_System"
            st.rerun()

def render_paperless_page():
    st.title("💻 台北市無紙化上傳系統")
    
    # 版面配置：左邊工作台，右邊作弊表
    col_workspace, col_cheat_sheet = st.columns([2, 1])

    with col_workspace:
        st.subheader("🛠️ 工程師的桌面")
        
        # --- 區域 A: 檔案轉換區 (The Converter) ---
        with st.container(border=True):
            st.write("#### 1️⃣ 文件編碼與轉檔機")
            st.info("請將「原始文件」配對正確的「NW 編碼」進行轉檔。")
            
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                # 選擇原始檔
                if st.session_state.raw_files:
                    selected_raw = st.selectbox("選擇原始文件", st.session_state.raw_files)
                else:
                    st.success("所有文件處理完畢！")
                    selected_raw = None
            
            with c2:
                # 選擇 NW 編碼
                nw_options = ["請選擇編碼..."] + list(NW_CODES.keys())
                selected_code = st.selectbox("賦予 NW 編碼", nw_options)
            
            with c3:
                st.write(" ") # 排版佔位
                st.write(" ") 
                # 按鈕邏輯
                if st.button("轉檔 ➡️", type="primary", disabled=(not selected_raw or selected_code == "請選擇編碼...")):
                    # 1. 從原始清單移除
                    st.session_state.raw_files.remove(selected_raw)
                    # 2. 產生新檔名 (模擬清理檔名)
                    clean_name = selected_raw.split('.')[0].replace("_核定版", "").replace("_用印掃描", "").replace("_A3", "")
                    new_filename = f"{selected_code}_{clean_name}.pdf"
                    
                    # 3. 加入已處理清單
                    st.session_state.processed_files.append(new_filename)
                    st.toast(f"✅ 成功轉檔為：{new_filename}")
                    st.rerun()

        # --- 區域 B: 傳送門 (The Portal) ---
        with st.container(border=True):
            st.write("#### 2️⃣ 建管處傳送門 (已轉檔文件)")
            
            if not st.session_state.processed_files:
                st.markdown("*目前沒有準備好的 PDF，請先在上方進行轉檔...*")
            else:
                # 多選清單
                files_to_send = st.multiselect(
                    "勾選要正式掛號的文件", 
                    st.session_state.processed_files,
                    default=st.session_state.processed_files
                )
                
                if st.button("🚀 送出電子簽章 (上傳)", type="primary"):
                    # 簡單的檢查邏輯
                    uploaded_codes = [f.split('_')[0] for f in files_to_send]
                    
                    # 檢查必備文件 (這裡假設 NW0100 和 NW3300 是必須的)
                    required = ["NW0100", "NW3300"]
                    missing = [code for code in required if code not in uploaded_codes]
                    
                    if missing:
                        st.error(f"❌ 退件：缺少必要文件！請檢查以下項目：{', '.join(missing)}")
                    else:
                        st.balloons()
                        st.success("✅ 掛號成功！案件已受理。")
                        time.sleep(2)
                        st.session_state.project_status["step"] = "Site_Inspection"
                        st.rerun()

    # 右側：Cheat Sheet
    with col_cheat_sheet:
        st.warning("HiCOS 憑證狀態")
        st.markdown("🟢 **已連線：工商憑證**")
        
        with st.expander("📖 NW 編碼對照表 (Cheat Sheet)", expanded=True):
            df = []
            for code, data in NW_CODES.items():
                df.append({"代碼": code, "名稱": data["name"]})
            st.dataframe(df, hide_index=True)
            
        st.markdown("---")
        st.markdown("#### 💡 提示")
        st.caption("1. 左上角：把「亂七八糟的檔案」配對「編碼」。")
        st.caption("2. 記得 `NW3300` 是施工計畫書。")
        st.caption("3. 轉檔完後，在下方勾選並送出。")

def render_site_page():
    st.title("🏗️ 現場放樣勘驗")
    st.markdown("### 目前階段：現場佈置與人員點名")
    
    col1, col2 = st.columns(2)
    with col1:
        # 讀取本地圖片 (請確保檔名為 site_simulation.png 且在同一資料夾)
        st.image("site_simulation.png", caption="工地現場模擬圖", use_container_width=True)
        
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
            st.balloons()

if __name__ == "__main__":
    main()