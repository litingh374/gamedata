import streamlit as st
import time
import os
from gamedata import REGIONS, PROJECT_TYPES, MASTER_TASKS, SETTING_OUT_STEPS, NW_CODES

# ==========================================
# 0. 核心狀態管理 (State Management)
# ==========================================
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "stage": "Launcher",  # 目前遊戲階段: Launcher -> MainGame
        "config": {},         # 專案設定 (地區、案型)
        "active_tasks": [],   # 根據設定生成的任務清單
        
        # --- 遊戲內進度變數 ---
        "plan_progress": 0,          # 施工計畫進度
        "is_demo_shield_active": False, # 拆除前鑑定 (護盾)
        "demo_progress": 0,          # 拆除現場進度
        "b5_closed": False,          # B5 結案狀態 (陷阱變數)
        "boss_hp": 100,              # BOSS 血量
        "logs": []                   # 遊戲紀錄
    }

def main():
    st.set_page_config(page_title="跑照大作戰：動態劇本版", layout="wide", page_icon="🏗️")
    
    # 路由控制器
    current_stage = st.session_state.game_state["stage"]
    
    if current_stage == "Launcher":
        render_launcher()
    elif current_stage == "MainGame":
        render_main_game()

# ==========================================
# 1. 遊戲大廳 (Game Launcher) - 選擇劇本
# ==========================================
def render_launcher():
    st.title("🏗️ 跑照大作戰：建立新專案")
    st.markdown("請設定本次專案的條件，這將決定遊戲的難度與流程。")
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("1. 選擇基地位置 (Region)")
            region = st.radio("法規管轄權", REGIONS, index=0)
            
            st.subheader("3. 特殊詞綴 (Modifiers)")
            is_mrt = st.checkbox("捷運沿線 (難度 +20%)")
            is_school = st.checkbox("學校周邊 (禁止噪音)")
            
        with col2:
            st.subheader("2. 選擇案型 (Project Type)")
            p_type = st.radio("開發類型", PROJECT_TYPES, index=0)
            
            # 動態顯示說明
            if "素地" in p_type:
                st.success("✅ **素地新建**：流程較單純，適合新手。\n\n無需執行拆除作業。")
            else:
                st.error("⚠️ **拆併建照**：高難度挑戰！\n\n包含完整的「拆除工程」與「廢棄物結案」流程。\n若未妥善處理 B5 結案，將導致放樣卡關。")

        st.markdown("---")
        if st.button("🚀 生成專案 (Start Game)", type="primary", use_container_width=True):
            initialize_game(region, p_type, is_mrt)

def initialize_game(region, p_type, is_mrt):
    """根據玩家選擇，從資料庫篩選任務"""
    
    # 1. 判斷標籤
    region_tag = "Taipei" if "台北" in region else "New Taipei"
    type_tag = "DEMO" if "拆併建" in p_type else "EMPTY"
    
    # 2. 篩選任務 (核心邏輯)
    generated_tasks = []
    for task in MASTER_TASKS:
        # 地區篩選: 任務是 ALL 或是符合當前地區
        match_region = task["region"] == "ALL" or task["region"] == region_tag
        
        # 案型篩選: 
        # 如果任務是 DEMO 專用，但我們選了素地 (EMPTY)，則不加入
        # 如果任務是 ALL，則都加入
        match_type = True
        if task["type"] == "DEMO" and type_tag == "EMPTY":
            match_type = False
            
        if match_region and match_type:
            generated_tasks.append(task)
    
    # 3. 寫入狀態
    st.session_state.game_state["config"] = {
        "region": region,
        "type": p_type,
        "is_mrt": is_mrt
    }
    st.session_state.game_state["active_tasks"] = generated_tasks
    st.session_state.game_state["stage"] = "MainGame"
    st.rerun()

# ==========================================
# 2. 主遊戲畫面 (Main Game) - 根據生成任務顯示
# ==========================================
def render_main_game():
    cfg = st.session_state.game_state["config"]
    st.title(f"🏗️ 專案執行中：{cfg['region']} - {cfg['type']}")
    
    # 顯示捷運標籤
    if cfg["is_mrt"]:
        st.warning("🚇 捷運沿線管制區：審查時間加倍")

    # 使用 Tab 分頁來呈現不同階段
    tab1, tab2, tab3 = st.tabs(["第一章：施工計畫", "第二章：拆除與整備", "終章：放樣勘驗"])
    
    # --- Tab 1: 施工計畫 (Plan Phase) ---
    with tab1:
        render_plan_phase()

    # --- Tab 2: 拆除與整備 (Demo Phase) ---
    with tab2:
        render_demo_phase()

    # --- Tab 3: 放樣勘驗 (BOSS Phase) ---
    with tab3:
        render_boss_phase()
        
    # 側邊欄紀錄
    with st.sidebar:
        st.write("📜 **專案日誌**")
        for log in st.session_state.game_state["logs"][-5:]:
            st.caption(log)
        
        if st.button("🔄 重置遊戲 (回大廳)"):
            st.session_state.clear()
            st.rerun()

# --- 各階段渲染邏輯 ---

def render_plan_phase():
    st.header("📋 施工計畫階段")
    
    # 從 active_tasks 撈出屬於 Plan 階段的任務
    plan_tasks = [t for t in st.session_state.game_state["active_tasks"] if t["phase"] == "Plan"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("待辦任務")
        for task in plan_tasks:
            st.checkbox(f"{task['name']}", key=task['id'], help=task['desc'])
    
    with col2:
        st.info("💡 提示：所有計畫通過後，才能進行拆除或放樣。")
        # 這裡簡化邏輯，假設勾選即完成進度
        progress = st.slider("模擬計畫審查進度", 0, 100, st.session_state.game_state["plan_progress"])
        st.session_state.game_state["plan_progress"] = progress

def render_demo_phase():
    st.header("🚜 拆除與基地整備")
    
    config_type = st.session_state.game_state["config"]["type"]
    
    # 邏輯分歧：素地 vs 拆併建
    if "素地" in config_type:
        st.success("✅ **素地新建模式**：")
        st.markdown("本案基地為空地，**無需執行拆除作業**。")
        st.markdown("您可以直接整理基地，準備放樣。")
        st.image("https://placeholder.co/600x200?text=Empty+Land+Ready", caption="基地狀況良好")
    else:
        # 拆併建模式 (您的核心設計)
        st.error("⚠️ **拆併建模式**：必須執行拆除作業！")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🛡️ 防禦措施")
            if st.button("執行：鄰房鑑定 (拆除前)"):
                st.session_state.game_state["is_demo_shield_active"] = True
                add_log("已完成鄰房鑑定，防護罩開啟。")
                st.success("已開啟防護罩！")
            
            st.markdown("---")
            st.subheader("🗑️ 廢棄物管理 (陷阱)")
            if st.button("申報：B5 拆除廢棄物結案"):
                st.session_state.game_state["b5_closed"] = True
                add_log("B5 廢棄物已結案。")
                st.success("✅ B5 已結案 (解除放樣卡關)")
        
        with c2:
            st.subheader("🏗️ 現場拆除")
            if not st.session_state.game_state["is_demo_shield_active"]:
                st.warning("⚠️ 警告：尚未進行鄰房鑑定！直接拆除可能引發鄰損賠償。")
            
            if st.button("執行：拆除作業"):
                if not st.session_state.game_state["is_demo_shield_active"]:
                    st.error("💥 發生鄰損！因為沒有鑑定報告，遭勒令停工！(Game Over 風險)")
                    add_log("❌ 未鑑定即拆除，發生鄰損事件！")
                else:
                    st.session_state.game_state["demo_progress"] = 100
                    st.success("拆除完成！基地已整平。")
                    add_log("拆除作業順利完成。")

def render_boss_phase():
    st.header("🏯 終章：放樣勘驗")
    
    # 核心邏輯：卡關檢查 (The Trap)
    config_type = st.session_state.game_state["config"]["type"]
    plan_ready = st.session_state.game_state["plan_progress"] >= 100
    
    # 檢查 1: 施工計畫是否完成
    if not plan_ready:
        st.warning("🔒 卡關：施工計畫尚未審查完成 (請回第一章)。")
        return

    # 檢查 2: 拆併建的 B5 陷阱
    if "拆併建" in config_type:
        # 必須拆除完成 且 B5 已結案
        demo_done = st.session_state.game_state["demo_progress"] >= 100
        b5_done = st.session_state.game_state["b5_closed"]
        
        if not demo_done:
            st.warning("🔒 卡關：現場舊屋尚未拆除 (請回第二章)。")
            return
        
        if not b5_done:
            st.error("🚫 **嚴重卡關：建管處拒絕受理！**")
            st.markdown("原因：系統查無 **B5 廢棄物結案** 紀錄。")
            st.caption("提示：請回到第二章辦理結案，或使用「特殊技能」延後結案。")
            return

    # 通過所有檢查，顯示 BOSS 戰
    st.success("🌟 文件與現場皆符合規定，准予掛號！")
    
    current_hp = st.session_state.game_state["boss_hp"]
    st.metric("放樣審查進度 (BOSS HP)", f"{current_hp}/100")
    
    if st.button("⚔️ 開始審查 (減少 HP)"):
        st.session_state.game_state["boss_hp"] = max(0, current_hp - 20)
        st.rerun()
    
    if st.session_state.game_state["boss_hp"] == 0:
        st.balloons()
        st.success("🏆 恭喜！取得放樣勘驗核准函！正式開工！")

def add_log(msg):
    st.session_state.game_state["logs"].append(f"{time.strftime('%H:%M')} - {msg}")

if __name__ == "__main__":
    main()