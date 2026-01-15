import streamlit as st
import time
# 確保 gamedata.py 和 app.py 在同一層目錄
from gamedata import TRIALS, ARCHITECT_ITEM

# --- 1. 遊戲初始化 (Session State) ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = {
        "has_permit": False,       # Stage 1: 是否取得建照
        "completed_trials": [],    # Stage 2: 已完成的試煉 ID
        "is_construction_started": False, # Stage 3: 是否已開工
        "inventory": []            # 背包
    }

def main():
    st.set_page_config(page_title="跑照大作戰：第一章", layout="wide", page_icon="🏗️")
    
    st.title("🏗️ 跑照大作戰：Level 1 開工之路")
    st.markdown("---")

    # 顯示 NPC 對話框 (依照進度變化)
    show_npc_dialog()

    # --- 核心儀表板 (Dashboard) ---
    # 分為左、中、右三區
    col_architect, col_trials, col_gate = st.columns([1, 2, 1])

    # === Stage 1: 建築師塔 (左) ===
    with col_architect:
        render_stage_1()

    # === Stage 2: 七大試煉 (中) ===
    with col_trials:
        render_stage_2()

    # === Stage 3: 開工大門 (右) ===
    with col_gate:
        render_stage_3()

    # --- 背包系統 (底部) ---
    st.markdown("---")
    with st.expander("🎒 隨身背包 (Inventory)", expanded=True):
        if not st.session_state.game_state["inventory"]:
            st.caption("背包空空如也...請開始執行任務！")
        else:
            # 顯示背包內的道具
            cols = st.columns(6)
            for i, item in enumerate(st.session_state.game_state["inventory"]):
                cols[i % 6].info(f"📄 {item}")

# --- 子功能函式區 ---

def show_npc_dialog():
    """根據當前狀態顯示 NPC 提示"""
    state = st.session_state.game_state
    
    if state["is_construction_started"]:
        st.success("工地主任：怪手進場啦！兄弟們上工了！ (Game Clear)")
    elif len(state["completed_trials"]) == 7:
        st.info("工地主任：文件都齊了！快去按那個「開工申報」按鈕！")
    elif state["has_permit"]:
        st.warning("建築師：建照拿去吧。接下來的七大關卡要靠你自己了，別讓業主等太久。")
    else:
        st.error("建築師：圖說還在修正中...你急也沒用，沒有【建造執照】你什麼都不能做。")

def render_stage_1():
    """渲染 Stage 1: 建築師塔"""
    st.header("🏛️ 建築師塔")
    
    has_permit = st.session_state.game_state["has_permit"]
    
    if has_permit:
        st.success("✅ 已取得：建造執照")
        # 如果您有上傳圖片，可以用 st.image("您的圖檔名.png")，否則使用預設圖
        st.image("https://placeholder.co/300x200?text=Building+Permit", caption="關鍵信物", use_container_width=True)
    else:
        st.info("🔒 任務鎖定中...")
        st.write("劇情：雖然案子拿到了，但缺少關鍵道具。")
        
        # 互動按鈕
        if st.button("索取信物：建造執照", type="primary"):
            with st.spinner("建築師簽核中..."):
                time.sleep(1.5) # 模擬等待
            st.session_state.game_state["has_permit"] = True
            st.session_state.game_state["inventory"].append(ARCHITECT_ITEM)
            st.toast("🎉 獲得道具：建造執照！解鎖 Stage 2")
            st.rerun()

def render_stage_2():
    """渲染 Stage 2: 七大試煉"""
    st.header("⚔️ 七大試煉")
    
    has_permit = st.session_state.game_state["has_permit"]
    completed = st.session_state.game_state["completed_trials"]
    
    # 進度條
    progress = len(completed) / 7
    st.progress(progress, text=f"準備進度：{len(completed)} / 7")

    if not has_permit:
        st.warning("🔒 請先完成 Stage 1 取得建照以解鎖此區域。")
        return
    
    for trial_id, data in TRIALS.items():
        # 決定卡片外觀
        is_done = trial_id in completed
        status_icon = "✅" if is_done else "🔲"
        
        # 利用 Streamlit 的 container 做成卡片感
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                # 定義顏色對應表 (將 gamedata 中的顏色代碼轉為 Markdown 顏色)
                color_map = {
                    "success": "green",
                    "primary": "blue",
                    "warning": "orange"
                }
                text_color = color_map.get(data['color'], "blue")
                
                # 使用 Markdown 顯示帶有顏色的標題
                st.markdown(f"**{status_icon} :{text_color}[{data['name']}]**")
                st.caption(f"{data['category']} | {data['desc']}")
            
            with c2:
                if not is_done:
                    # 修正點：按鈕 type 統一設為 "primary" 或 "secondary"
                    if st.button("執行", key=trial_id, type="primary"):
                        process_trial(trial_id, data)

def process_trial(trial_id, data):
    """處理按下任務按鈕後的邏輯"""
    # 模擬隨機事件
    if trial_id == "T06": # 鄰房鑑定
        with st.spinner("正在聯絡阿嬤開門..."):
            time.sleep(1)
            st.toast("👵 隨機事件：阿嬤不在家，多花了一天...", icon="🐢")
    
    elif trial_id == "T07": # 拆除施工計畫 (魔王)
        with st.spinner("審查委員提問中..."):
            time.sleep(1.5)
            st.toast("👿 魔王關卡：消耗 10 點智力值回復委員意見！", icon="🧠")
    else:
        # 一般任務
        with st.spinner(f"正在執行：{data['name']}..."):
            time.sleep(0.5)

    # 完成任務
    st.session_state.game_state["completed_trials"].append(trial_id)
    # 獲得對應道具 (簡單模擬)
    st.session_state.game_state["inventory"].append(f"{data['name']} 核准函")
    st.rerun()

def render_stage_3():
    """渲染 Stage 3: 開工大門"""
    st.header("🚪 開工大門")
    
    completed_count = len(st.session_state.game_state["completed_trials"])
    is_started = st.session_state.game_state["is_construction_started"]
    
    if is_started:
        st.balloons()
        st.success("🎉 GAME CLEAR！")
        st.write("已進入施工階段。")
        # 如果有上傳開工圖，可以改用 st.image("開工圖.png")
        st.image("https://placeholder.co/300x400?text=Construction+Start", caption="怪手進場", use_container_width=True)
    
    else:
        # 判斷是否滿足 IF (Items_Count == 7)
        if completed_count == 7:
            st.success("🔓 封印解除！")
            st.write("所有文件齊全，準備申報。")
            
            if st.button("🚀 申報開工 (Submit)", type="primary", use_container_width=True):
                with st.spinner("文件飛入政府機關...蓋章中..."):
                    time.sleep(2)
                st.session_state.game_state["is_construction_started"] = True
                st.rerun()
        else:
            st.error(f"🔒 大門深鎖 ({completed_count}/7)")
            st.caption("請先收集完所有 Stage 2 的核准文件。")
            st.button("🚫 申報開工", disabled=True, use_container_width=True)

if __name__ == "__main__":
    main()