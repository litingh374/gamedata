import streamlit as st
import time
import os
from gamedata import TRIALS, ARCHITECT_ITEM, NW_CODES

# --- 1. 遊戲初始化 (Session State) ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "current_stage": "Level_1_Dashboard",  # 控制目前顯示哪個大關卡
        "has_permit": False,
        "completed_trials": [],
        "inventory": [],
        
        # Level 2 無紙化專用狀態
        "paperless_raw_files": [
            "施工計畫書_核定版.docx", "開工申報書_用印掃描.jpg", 
            "配筋圖_A3.dwg", "圍籬綠美化設計圖.png", 
            "工地主任證書_含勞保.pdf", "這是不相關的自拍照.jpg"
        ],
        "paperless_processed_files": [],
        "paperless_completed": False,

        # Level 3 開工狀態
        "is_construction_started": False
    }

def main():
    st.set_page_config(page_title="跑照大作戰：完整版", layout="wide", page_icon="🏗️")
    
    # 路由控制器 (Router)
    # 加上 try-except 防止因版本更新導致的 key error
    try:
        stage = st.session_state.game_state["current_stage"]
    except KeyError:
        # 如果發生錯誤，重置狀態
        st.warning("偵測到舊的存檔結構，正在重置遊戲...")
        st.session_state.clear()
        st.rerun()
    
    if stage == "Level_1_Dashboard":
        render_level_1_dashboard()
    elif stage == "Level_2_Paperless_Minigame":
        render_level_2_minigame()
    elif stage == "Level_3_Site_Inspection":
        render_level_3_site()

# ==========================================
# Level 1: 核心儀表板 (The Headquarters)
# ==========================================
def render_level_1_dashboard():
    st.title("🏗️ 跑照大作戰：Level 1 開工之路")
    st.caption("目標：收集所有文件，解鎖開工大門。")
    st.markdown("---")

    col_architect, col_trials, col_gate = st.columns([1, 2, 1])

    # --- 左：建築師塔 ---
    with col_architect:
        st.header("🏛️ 建築師塔")
        if st.session_state.game_state["has_permit"]:
            st.success("✅ 已取得：建造執照")
        else:
            st.info("🔒 任務鎖定中...")
            if st.button("索取信物：建造執照", type="primary"):
                with st.spinner("建築師簽核中..."):
                    time.sleep(1)
                st.session_state.game_state["has_permit"] = True
                st.session_state.game_state["inventory"].append(ARCHITECT_ITEM)
                st.rerun()

    # --- 中：七大試煉 ---
    with col_trials:
        st.header("⚔️ 七大試煉")
        
        if not st.session_state.game_state["has_permit"]:
            st.warning("🔒 請先取得建照解鎖。")
        else:
            completed = st.session_state.game_state["completed_trials"]
            st.progress(len(completed) / 7, text=f"完成度：{len(completed)}/7")

            for trial_id, data in TRIALS.items():
                is_done = trial_id in completed
                status_icon = "✅" if is_done else "🔲"
                
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        # 顏色映射
                        color_map = {"success": "green", "primary": "blue", "warning": "orange"}
                        text_color = color_map.get(data['color'], "blue")
                        st.markdown(f"**{status_icon} :{text_color}[{data['name']}]**")
                        st.caption(f"{data['category']} | {data['desc']}")
                    with c2:
                        if not is_done:
                            # 特殊邏輯：T04 觸發無紙化小遊戲
                            if trial_id == "T04":
                                if st.button("進入系統", key=trial_id, type="primary"):
                                    st.session_state.game_state["current_stage"] = "Level_2_Paperless_Minigame"
                                    st.rerun()
                            else:
                                if st.button("執行", key=trial_id, type="primary"):
                                    process_trial_logic(trial_id, data)

    # --- 右：開工大門 ---
    with col_gate:
        st.header("🚪 開工大門")
        if len(st.session_state.game_state["completed_trials"]) == 7:
            st.success("🔓 封印解除！")
            if st.button("🚀 申報開工", type="primary", use_container_width=True):
                st.balloons()
                time.sleep(2)
                st.session_state.game_state["current_stage"] = "Level_3_Site_Inspection"
                st.rerun()
        else:
            st.error("🔒 大門深鎖")
            st.button("🚫 申報開工", disabled=True, use_container_width=True)

    # --- 底部：背包 ---
    st.markdown("---")
    with st.expander("🎒 背包狀態", expanded=False):
        st.write(st.session_state.game_state["inventory"])

def process_trial_logic(trial_id, data):
    """處理 Level 1 的簡單任務邏輯"""
    if trial_id == "T06":
        with st.spinner("聯絡阿嬤開門..."):
            time.sleep(0.5)
            st.toast("👵 阿嬤不在家，延遲一天！", icon="🐢")
    
    st.session_state.game_state["completed_trials"].append(trial_id)
    st.session_state.game_state["inventory"].append(f"{data['name']} 核准函")
    st.rerun()

# ==========================================
# Level 2: 無紙化虛擬桌面 (The Minigame)
# ==========================================
def render_level_2_minigame():
    st.title("💻 台北市無紙化上傳系統")
    if st.button("🔙 放棄並返回儀表板"):
        st.session_state.game_state["current_stage"] = "Level_1_Dashboard"
        st.rerun()
        
    col_workspace, col_cheat = st.columns([2, 1])

    with col_workspace:
        st.subheader("🛠️ 工程師桌面")
        with st.container(border=True):
            st.info("任務：將原始檔轉碼為 PDF 並上傳。")
            c1, c2, c3 = st.columns([2,2,1])
            
            # 1. 選擇原始檔
            raw_files = st.session_state.game_state["paperless_raw_files"]
            selected_raw = c1.selectbox("原始文件", raw_files) if raw_files else None
            
            # 2. 選擇編碼
            selected_code = c2.selectbox("NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
            
            # 3. 轉檔按鈕
            if c3.button("轉檔 ➡️", type="primary", disabled=not selected_raw):
                st.session_state.game_state["paperless_raw_files"].remove(selected_raw)
                clean_name = selected_raw.split('.')[0].replace("_核定版","").replace("_A3","")
                new_name = f"{selected_code}_{clean_name}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.toast(f"已轉檔：{new_name}")
                st.rerun()

        with st.container(border=True):
            st.write("#### 準備上傳的文件")
            processed = st.session_state.game_state["paperless_processed_files"]
            to_upload = st.multiselect("勾選上傳", processed, default=processed)
            
            if st.button("🚀 送出電子簽章", type="primary", use_container_width=True):
                # 簡易檢查：必須要有施工計畫書 (NW3300)
                if any("NW3300" in f for f in to_upload):
                    st.success("✅ 系統審核通過！")
                    time.sleep(1)
                    # 標記 T04 完成
                    if "T04" not in st.session_state.game_state["completed_trials"]:
                        st.session_state.game_state["completed_trials"].append("T04")
                        st.session_state.game_state["inventory"].append("無紙化掛號序號")
                    
                    st.session_state.game_state["current_stage"] = "Level_1_Dashboard"
                    st.rerun()
                else:
                    st.error("❌ 退件：缺少 NW3300 施工計畫書！")

    # --- 右側：Cheat Sheet (改成直式表格) ---
    with col_cheat:
        st.markdown("🟢 **HiCOS 已連線**")
        
        # 將 NW_CODES 字典轉換為列表，讓 Streamlit 能夠以「列」的方式顯示
        cheat_sheet_data = []
        for code, info in NW_CODES.items():
            row = {
                "代碼": code,
                "名稱": info["name"],
                "類型": info["type"]
            }
            # 為了讓表格更簡潔，可以只顯示重點欄位
            cheat_sheet_data.append(row)
        
        st.write("▼ NW 編碼對照表")
        # use_container_width=True 讓表格填滿欄位寬度
        st.dataframe(cheat_sheet_data, hide_index=True, use_container_width=True)

# ==========================================
# Level 3: 工地放樣現場 (The Construction Site)
# ==========================================
def render_level_3_site():
    st.title("🏗️ 現場放樣勘驗")
    st.success("恭喜！已進入實質動工階段。")
    
    col1, col2 = st.columns(2)
    with col1:
        # 嘗試讀取本地圖片，若無則顯示替代圖
        # 記得確認您的 GitHub 上有 site_simulation.png
        img_path = "site_simulation.png"
        if os.path.exists(img_path):
            st.image(img_path, caption="工地模擬圖", use_container_width=True)
        else:
            st.warning("⚠️ 找不到 site_simulation.png，請確認 Github 上傳。")
            st.image("https://placeholder.co/600x400?text=Construction+Site", use_container_width=True)
            
        if st.button("檢查防溢座"):
            st.info("✅ 高度 60cm，合格！")

    with col2:
        st.subheader("人員點名 (QTE)")
        c_p1, c_p2 = st.columns(2)
        if c_p1.button("召喚工地主任"): st.write("👷 主任到！")
        if c_p2.button("召喚技師"): st.write("👷‍♀️ 技師到！")
        
        if st.button("📸 拍攝大合照", type="primary"):
            st.balloons()
            st.success("🎉 放樣勘驗通過！進入結構體工程 (待續...)")

if __name__ == "__main__":
    main()