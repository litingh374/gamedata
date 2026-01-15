import streamlit as st
import time
from gamedata import REGIONS, PROJECT_TYPES, TRIALS, GEMS, SETTING_OUT_STEPS, NW_CODES

# ==========================================
# 0. 核心狀態管理
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",
        "config": {},
        
        # Ch1: 開工
        "completed_trials": [],
        "commencement_done": False,
        "doing_paperless": False, # 控制小遊戲切換
        
        # 無紙化檔案狀態
        "paperless_raw_files": [
            "施工計畫書_核定版.docx", "開工申報書_用印掃描.jpg", 
            "配筋圖_A3.dwg", "圍籬綠美化設計圖.png", 
            "工地主任證書_含勞保.pdf", "這是不相關的自拍照.jpg"
        ],
        "paperless_processed_files": [],
        
        # Ch2: 施工計畫
        "collected_gems": [],
        "plan_approved": False,
        
        # Ch3: 拆除 (條件式)
        "is_demo_shield_active": False,
        "demo_progress": 0,
        "b5_closed": False,
        "demo_phase_passed": False,
        
        # Ch4: 導溝
        "guide_wall_progress": 0,
        "guide_wall_inspected": False,
        
        # Ch5: 放樣 BOSS
        "boss_hp": 100,
        "logs": []
    }

def main():
    st.set_page_config(page_title="跑照大作戰：完全修正版", layout="wide", page_icon="🏗️")
    
    if st.session_state.game_state["stage"] == "Launcher":
        render_launcher()
    else:
        render_main_game()

# ==========================================
# 遊戲大廳
# ==========================================
def render_launcher():
    st.title("🏗️ 跑照大作戰：建立新專案")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            region = st.radio("基地位置", REGIONS)
            is_mrt = st.checkbox("捷運沿線管制")
        with col2:
            p_type = st.radio("開發類型", PROJECT_TYPES)
            if "拆併建" in p_type:
                st.error("⚠️ 拆併建模式：將開啟 Ch3 拆除章節與 B5 陷阱！")
            else:
                st.success("✅ 素地新建：Ch3 拆除章節將自動跳過。")
        
        if st.button("🚀 生成專案", type="primary", use_container_width=True):
            st.session_state.game_state["config"] = {"region": region, "type": p_type, "is_mrt": is_mrt}
            
            # 若為素地，預設拆除階段通過，且無 B5 問題
            if "素地" in p_type:
                st.session_state.game_state["demo_phase_passed"] = True
                st.session_state.game_state["b5_closed"] = True
            
            st.session_state.game_state["stage"] = "MainGame"
            st.rerun()

# ==========================================
# 主遊戲介面
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    
    # 檢查是否正在進行無紙化小遊戲
    if st.session_state.game_state["doing_paperless"]:
        render_paperless_minigame()
        return

    st.title(f"🏗️ 專案執行中：{cfg['type']}")
    
    tabs = st.tabs(["Ch1 開工申報", "Ch2 施工計畫", "Ch3 拆除整備", "Ch4 導溝勘驗", "Ch5 放樣 BOSS"])
    
    with tabs[0]: render_chapter_1()
    with tabs[1]: render_chapter_2()
    with tabs[2]: render_chapter_3()
    with tabs[3]: render_chapter_4()
    with tabs[4]: render_chapter_5()

    with st.sidebar:
        st.write("📜 **專案日誌**")
        for log in st.session_state.game_state["logs"][-5:]:
            st.caption(log)
        if st.button("🔄 重置遊戲"):
            st.session_state.clear()
            st.rerun()

# --- Ch1: 開工申報 ---
def render_chapter_1():
    st.header("📂 第一章：開工申報")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("七大試煉")
        completed = st.session_state.game_state["completed_trials"]
        for tid, data in TRIALS.items():
            is_done = tid in completed
            icon = "✅" if is_done else "🔲"
            
            if st.button(f"{icon} {data['name']}", key=tid, disabled=is_done):
                if tid == "T04":
                    # 觸發無紙化小遊戲
                    st.session_state.game_state["doing_paperless"] = True
                    st.rerun()
                else:
                    st.session_state.game_state["completed_trials"].append(tid)
                    add_log(f"完成試煉：{data['name']}")
                    st.rerun()
    with col2:
        st.subheader("狀態")
        st.progress(len(completed) / 7, text=f"{len(completed)}/7")
        if len(completed) == 7:
            if st.button("🚀 申報開工", type="primary", use_container_width=True):
                st.session_state.game_state["commencement_done"] = True
                st.balloons()
                add_log("第一章通關！開工申報完成。")

# --- 無紙化小遊戲 (嵌入模組) ---
def render_paperless_minigame():
    st.title("💻 台北市無紙化上傳系統")
    st.info("任務：將左側原始檔配對正確編碼，轉成 PDF 後上傳。")
    if st.button("🔙 放棄並返回"):
        st.session_state.game_state["doing_paperless"] = False
        st.rerun()

    col_ws, col_cheat = st.columns([2, 1])
    with col_ws:
        st.subheader("🛠️ 工程師桌面")
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            raw_files = st.session_state.game_state["paperless_raw_files"]
            selected_raw = c1.selectbox("原始文件", raw_files) if raw_files else None
            selected_code = c2.selectbox("NW 編碼", ["請選擇..."] + list(NW_CODES.keys()))
            
            if c3.button("轉檔 ➡️", type="primary", disabled=not selected_raw):
                st.session_state.game_state["paperless_raw_files"].remove(selected_raw)
                clean_name = selected_raw.split('.')[0].replace("_核定版","").replace("_A3","")
                new_name = f"{selected_code}_{clean_name}.pdf"
                st.session_state.game_state["paperless_processed_files"].append(new_name)
                st.toast(f"已轉檔：{new_name}")
                st.rerun()

        with st.container(border=True):
            st.write("#### 準備上傳")
            processed = st.session_state.game_state["paperless_processed_files"]
            to_upload = st.multiselect("勾選上傳", processed, default=processed)
            if st.button("🚀 送出電子簽章", type="primary", use_container_width=True):
                if any("NW3300" in f for f in to_upload):
                    st.success("✅ 系統審核通過！")
                    time.sleep(1)
                    if "T04" not in st.session_state.game_state["completed_trials"]:
                        st.session_state.game_state["completed_trials"].append("T04")
                    st.session_state.game_state["doing_paperless"] = False
                    add_log("無紙化上傳成功。")
                    st.rerun()
                else:
                    st.error("❌ 缺少 NW3300 施工計畫書！")

    with col_cheat:
        st.markdown("🟢 **HiCOS 已連線**")
        cheat_data = [{"代碼": k, "名稱": v["name"]} for k, v in NW_CODES.items()]
        st.dataframe(cheat_data, hide_index=True, use_container_width=True)

# --- Ch2: 施工計畫 ---
def render_chapter_2():
    st.header("📜 第二章：施工計畫")
    if not st.session_state.game_state["commencement_done"]:
        st.warning("🔒 鎖定中：請先完成第一章。")
        return
    
    col1, col2 = st.columns([2, 1])
    collected = st.session_state.game_state["collected_gems"]
    with col1:
        st.subheader("六大寶石")
        cols = st.columns(3)
        for i, (key, data) in enumerate(GEMS.items()):
            with cols[i % 3]:
                is_got = key in collected
                btn_type = "secondary" if is_got else "primary"
                if st.button(f"獲取\n{data['name']}", key=key, type=btn_type, disabled=is_got):
                    st.session_state.game_state["collected_gems"].append(key)
                    st.rerun()
    with col2:
        st.subheader("狀態")
        if len(collected) == 6:
            if st.button("✨ 核定計畫", type="primary"):
                st.session_state.game_state["plan_approved"] = True
                add_log("施工計畫核定。")
        else:
            st.write(f"收集：{len(collected)}/6")

# --- Ch3: 拆除整備 ---
def render_chapter_3():
    st.header("🚜 第三章：拆除整備")
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 鎖定中：請先完成第二章。")
        return

    config_type = st.session_state.game_state["config"]["type"]
    if "素地" in config_type:
        st.success("✅ 素地新建：無需拆除，本章節自動通過。")
        return

    st.error("⚠️ 拆併建模式：")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("鄰房鑑定 (開啟護盾)"):
            st.session_state.game_state["is_demo_shield_active"] = True
            st.success("護盾 ON")
        if st.button("B5 廢棄物結案"):
            st.session_state.game_state["b5_closed"] = True
            st.success("B5 已結案")
            add_log("B5 結案完成。")
    with c2:
        if st.button("執行拆除"):
            if not st.session_state.game_state["is_demo_shield_active"]:
                st.error("💥 未鑑定即拆除！發生鄰損！")
                add_log("發生鄰損事件。")
            else:
                st.session_state.game_state["demo_progress"] = 100
                st.success("拆除完成！")

    if st.session_state.game_state["demo_progress"] >= 100:
        st.session_state.game_state["demo_phase_passed"] = True
        st.success("拆除階段完成！")

# --- Ch4: 導溝勘驗 (邏輯修正版) ---
def render_chapter_4():
    st.header("🧱 第四章：導溝勘驗")
    
    # === 核心修正：雙重檢查 ===
    # 1. 確保第二章 (施工計畫) 真的做完了
    if not st.session_state.game_state["plan_approved"]:
        st.warning("🔒 鎖定中：請先完成第二章「施工計畫」。")
        return
    # 2. 確保第三章 (拆除) 通過 (素地自動通過，拆併建需手動)
    if not st.session_state.game_state["demo_phase_passed"]:
        st.warning("🔒 鎖定中：請先完成第三章「拆除整備」。")
        return
    # ==========================

    col1, col2 = st.columns(2)
    with col1:
        gw_prog = st.session_state.game_state["guide_wall_progress"]
        st.progress(gw_prog / 100, text=f"進度: {gw_prog}%")
        if gw_prog < 100:
            if st.button("施工：挖溝&澆置"):
                st.session_state.game_state["guide_wall_progress"] += 50
                st.rerun()
    with col2:
        if gw_prog >= 100:
            if st.button("📞 申報導溝勘驗", type="primary"):
                # 陷阱檢查：如果是拆併建，B5 必須已結案
                config_type = st.session_state.game_state["config"]["type"]
                b5_ok = st.session_state.game_state["b5_closed"]
                
                if "拆併建" in config_type and not b5_ok:
                    st.error("🚫 退件！拆除廢棄物 (B5) 尚未結案。")
                else:
                    st.session_state.game_state["guide_wall_inspected"] = True
                    st.balloons()
                    add_log("導溝勘驗通過。")

# --- Ch5: 放樣 BOSS ---
def render_chapter_5():
    st.header("🏯 終章：放樣勘驗")
    if not st.session_state.game_state["guide_wall_inspected"]:
        st.error("🔒 卡關！請先完成第四章。")
        return

    st.success("🌟 准予掛號！")
    hp = st.session_state.game_state["boss_hp"]
    st.metric("BOSS HP", f"{hp}/100")
    if st.button("⚔️ 發動攻擊"):
        st.session_state.game_state["boss_hp"] = max(0, hp - 20)
        st.rerun()
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜通關！准予放樣！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()